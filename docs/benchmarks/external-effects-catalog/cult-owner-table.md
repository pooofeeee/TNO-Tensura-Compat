# Cult of Azazel — native semantic review complete

Installed cultofazazelneo-1.1.3.1; raw Minecraft1.21.1; installed NeoForge21.1.244. Static research only.

51 mechanic/package records; 64 distinct delivery/predicate cases; no unresolved native REVIEW_REQUIRED items.

Exact behavior, formulas, source chains, exclusions and references: [machine-readable review](mod-reviews/cultofazazel.json).
Conditional equipment mappings: [compatibility attribution](compat-findings/cultofazazel.json).

| Mechanic/package | Class | Primary future source | Distinct paths |
|---|---|---|---|
| Manipulation | CUSTOM_CONTROL | netherman:manipulator_stick | 4 |
| Manipulator Stick pull | CUSTOM_CONTROL | netherman:manipulator_stick | 1 |
| Held-stick fleeing | CUSTOM_CONTROL | netherman:manipulator_stick | 1 |
| Owned Wither Skeleton targeting | CUSTOM_CONTROL | netherman:manipulator_stick | 1 |
| Chance Totem rescue | BINARY_MECHANIC | Chance Totem in main/offhand | 2 |
| Azazel Trophy charges and regeneration | CUSTOM_RESOURCE | netherman:azazel_trophy | 1 |
| Mask fire immunity | BINARY_MECHANIC | Any Azazel Trophy stage in HEAD | 1 |
| Crimson Arrow ricochet | VANILLA_LIKE_EXTENDED | Vanilla Bow + netherman:crimson_arrow | 2 |
| Azazel hit-counter protection | BINARY_MECHANIC | netherman:azazel | 2 |
| Azazel terminal threshold and discard | BINARY_MECHANIC | netherman:azazel | 1 |
| Azazel mercy and forced facing | CUSTOM_CONTROL | Azazel + iron/diamond/netherite sword or axe | 1 |
| Azazel Wind | CUSTOM_CONTROL | netherman:azazel | 1 |
| Azazel Pull | CUSTOM_CONTROL | netherman:azazel | 1 |
| Azazel Launch | CUSTOM_CONTROL | netherman:azazel | 1 |
| Azazel Wheel | CUSTOM_CONTROL | netherman:azazel | 1 |
| Midas expanding fire ring | VANILLA_COMPOSITE | netherman:azazel | 1 |
| Midas inventory replacement | CUSTOM_RESOURCE | netherman:azazel | 1 |
| Azazel prison terrain | CUSTOM_CONTROL | netherman:azazel | 1 |
| Azazel native Evoker Fangs | VANILLA_DIRECT | netherman:azazel | 1 |
| Laser moving hazard | VANILLA_LIKE_EXTENDED | netherman:azazel | 1 |
| Believer protection | BINARY_MECHANIC | Azazel + netherman:believer | 1 |
| Believer sickness | CUSTOM_CONTROL | Gunpowder / golden apple + netherman:believer | 2 |
| Believer boss healing | VANILLA_DIRECT | netherman:believer near Azazel | 1 |
| Believer Bad Omen and Azazel aggro | VANILLA_LIKE_EXTENDED | netherman:believer killed by a Player-owned source | 2 |
| Guardian rapid melee | CUSTOM_DAMAGE | netherman:guardian | 1 |
| Guardian mega-punch | VANILLA_LIKE_EXTENDED | netherman:guardian | 1 |
| Welcomer Guardian buff | CUSTOM_STATUS | Welcomer + targeted Guardian within30 | 1 |
| Gilded Golem healing pull | CUSTOM_RESOURCE | netherman:gilded_golem | 2 |
| Gilded Golem extra launch | VANILLA_LIKE_EXTENDED | netherman:gilded_golem | 1 |
| Wither | VANILLA_DIRECT | netherman:statue_bossunit | 4 |
| Slowness | VANILLA_DIRECT | netherman:statue_bossunit | 5 |
| Poison | VANILLA_DIRECT | netherman:statue_bossunit | 2 |
| Unluck | VANILLA_DIRECT | netherman:statue_bossunit | 2 |
| Darkness | VANILLA_DIRECT | netherman:statue_bossunit | 3 |
| Statue observation lock | CUSTOM_CONTROL | netherman:statue_entity | 1 |
| Prisoner capture and release | CUSTOM_CONTROL | netherman:manipulator + minecraft:villager | 2 |
| Manipulator Ghastly death branch | CUSTOM_DAMAGE | netherman:manipulator + netherman:ghastly | 1 |
| Crimson Honey bounce | VANILLA_LIKE_EXTENDED | netherman:crimson_honey_block | 2 |
| Copied Honey movement/jump factors | VANILLA_DIRECT | netherman:crimson_honey_block | 2 |
| Void contact damage | VANILLA_DIRECT | netherman:void_corner | 1 |
| Pointed Blackstone tip fall | VANILLA_DIRECT | netherman:pointed_blackstone | 1 |
| CrimsonWeb opening wave | CUSTOM_CONTROL | netherman:crimson_web | 1 |
| Entrance opening wave | CUSTOM_CONTROL | netherman:entrance | 1 |
| Traphive contact/projectile gate | CUSTOM_CONTROL | netherman:traphive | 2 |
| Grand Door collision and aim movement | CUSTOM_CONTROL | netherman:grand_door | 2 |
| Mansion view-distance fog | VANILLA_LIKE_EXTENDED | netherman:mansion_nether | 1 |
| Registered entity fire immunity | BINARY_MECHANIC | Eight registered fire-immune Cult types | 1 |
| Explicit knockback/push rejection | BINARY_MECHANIC | netherman:doctor | 5 |
| Ghastly fall rejection | BINARY_MECHANIC | netherman:ghastly | 1 |
| Blacksmith paid durability repair | CUSTOM_RESOURCE | netherman:blacksmith + Netherite Scrap + damageable non-armor item | 1 |
| Doctor parameterized native potion | VANILLA_LIKE_EXTENDED | Doctor-produced minecraft:potion | 2 |

## Classification counts

- BINARY_MECHANIC: 8
- CUSTOM_CONTROL: 17
- CUSTOM_DAMAGE: 2
- CUSTOM_RESOURCE: 4
- CUSTOM_STATUS: 1
- VANILLA_COMPOSITE: 1
- VANILLA_DIRECT: 10
- VANILLA_LIKE_EXTENDED: 8

## Future source cover

25 fixture families cover all 64 named cases. This is an explicit local setup cover, not a proved minimum number of actors, spawn eggs or test runs. Global minimization remains R3.

- manipulator_stick: manipulation_melee, stick_active_pull, stick_passive_flee, stick_owned_summon, owned_skeleton_wither
- chance_totem: chance_hand, chance_curio
- azazel_trophy_family: mask_death_repair, mask_fire
- crimson_arrow_with_bow_and_crossbow: ricochet_bow, ricochet_crossbow
- azazel: azazel_shield, azazel_terminal, azazel_mercy, azazel_wind, azazel_pull, azazel_launch, azazel_wheel, azazel_midas, azazel_prison, azazel_fangs, azazel_lasers, azazel_altar_admission
- believer_with_azazel: believer_pray_protection, believer_sickness_item, believer_heal, believer_death_omen
- doctor_with_believer_and_potions: believer_sickness_doctor, doctor_push_guard, doctor_duration_potion, doctor_instant_potion
- guardian_with_welcomer: guardian_rapid, guardian_mega, welcomer_aura, welcomer_push_guard
- gilded_golem_unowned_and_player_created: golem_healing_unowned, golem_healing_creator, golem_melee
- statue_bossunit: bossunit_random_holder, statue_bossunit_push_guard
- statue_entity: statue_watch
- manipulator_with_villager_piglin_ghastly: manipulation_cast, manipulator_skeleton_wither, villager_capture_release, piglin_capture_release, ghastly_conversion_death
- crimson_honey_block: crimson_honey_landing, crimson_honey_side, crimson_honey_block_properties
- eye: eye_properties
- ordinary_void_family: void_contact
- pointed_blackstone: pointed_tip_fall
- crimson_web: crimson_web_interaction
- entrance: entrance_interaction
- traphive_with_native_projectile: traphive_contact, traphive_projectile
- grand_door_with_guardian_and_tamed_ghastly: grand_door_use, grand_door_guardian
- mansion_nether_structure: mansion_visibility
- blacksmith_and_repair_items: blacksmith_push_guard, blacksmith_paid_repair
- ghastly: ghastly_fall_guard
- laser_descendant: laser_push_guard
- registered_fire_recipient_set: type_fire_flag

## Exclusions

- **zones**: Empty ZoneEffect subclasses have no attribute, damage or control implementation. Totemus and Azazel manage actual markers; ClientZoneAmbientEvents uses them for titles/audio. Leaving Totemus radius does not itself clear; type3 removes in its own scan. Doctor can randomly produce them, but this does not create combat semantics.
- **honey_bottle**: 40-tick food use nutrition6/saturationModifier.1/alwaysEdible, bottle return. Item subclass does not call HoneyBottleItem or removeEffectsCuredBy(HONEY); no native Poison cure. useOn converts vanilla Honey to Crimson Honey and coating recipe makes1..5 Crimson Arrows with one bottle. Future source alternatives link to their block/projectile records; ordinary food/saturation is not a new combat formula.
- **nether_void_variants**: Nether-suffixed blocks return empty collision and their block entities have empty controller registration; no entityInside magic/Darkness like ordinary Void variants.
- **ordinary_summons_arrows**: Ordinary arrows, spawn eggs, altar/NetherSpawner creation, passive/Midas summons and Believer-death Statue are preserved in source_chains. Native descendants keep their own mechanics. Normal melee/projectile damage without an additional rule is not a new special effect.
- **statue_stand_and_decoration**: Statue Stand and empty block entities supply geometry/rendering, not Statue entity attacks. Blackstone columns/axon/plant, trophy display and mosaic blocks are ordinary geometry/support/decor; prison actively placed terrain is separately counted.
- **ghastly_husbandry**: Taming/nesting/pollination/honey are husbandry. Hive stores full Ghastly NBT up to5 then reloads it; not fresh prisoner replacement. No attack goal/new soul or HP drain. Tamed Ghastly is a prerequisite for the separately cataloged Guardian door path.
- **npc_trade_and_mining**: Trader loot tables create ordinary items/enchants; Blacksmith raw-gold disassembly is acquisition. Blacksmith durability repair and Doctor actual effect-potion generation are separately counted. Prisoner mining animation/sounds do not destroy mining blocks. Hints, anvil-looking and note UI are not debuffs.
- **cosmetic_phases**: Azazel phase thresholds <=50%/<=25% drive synchronized visuals but do not scale shown attack formulas. Guardian death Weakness sound is not Weakness; Launch/death explosion particles are not damage explosions. Entity models/renderer bone rotations, emissive/hint layers, boss bars, overlays and fog color are visual; actual player input/aim and fog distance changes are separately counted.

## Limits and next task

All requested native ambiguity is resolved. Known compatibility effects are conditional; full-pack runtime/resource precedence remains outside this review. No damage amount is an observed HP/SHP result. Phase 6 and production are unchanged. After commit/push/live verification, next mod is Royal Variations; R2 as a whole remains incomplete.
