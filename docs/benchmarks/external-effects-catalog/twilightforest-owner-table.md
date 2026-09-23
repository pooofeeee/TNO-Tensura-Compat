# Twilight Forest — final semantic owner table

**COMPLETE: 219 distinct combat mechanics / 640 native delivery paths; 40/40 custom DamageTypes USED; 0 REVIEW_REQUIRED; 0 native ambiguities.** Static only. [Final review](twilightforest-final-review.md), [complete source/path/provenance](mod-reviews/twilightforest.json), [future fixtures](twilightforest-future-runtime-fixtures.json). Historical research sections and original draft counts are preserved in their checkpoint artifacts; this table is the current deduplicated combat scope.

| Mechanic | Classification | Native paths | Primary source |
|---|---|---:|---|
| Frosted status package | CUSTOM_STATUS | 15 | twilightforest:ice_sword used by Player |
| Ice Bomb attack and lingering freeze zone | CUSTOM_DAMAGE | 8 | twilightforest:ice_bomb used by Player |
| Lich shield resource | CUSTOM_RESOURCE | 14 | Player.attack native Bolt redirect |
| Lich HP admission and projectile defense | BINARY_MECHANIC | 18 | Player.attack native Bolt redirect |
| Lich Bolt and reflection | CUSTOM_DAMAGE | 4 | Player.attack native Bolt redirect |
| Lich Bomb explosion | CUSTOM_DAMAGE | 3 | Main Lich and clone Bomb goals |
| Lich phase resources and summons | CUSTOM_RESOURCE | 4 | Main Lich and clone Bolt goals |
| Lich mob consumption and healing | CUSTOM_RESOURCE | 2 | Damaged Lich and visible poppable Mob |
| Lich combat teleport | CUSTOM_CONTROL | 1 | Native Lich combat/home teleport triggers |
| Lich Minion retaliation buffs | VANILLA_LIKE_EXTENDED | 2 | Phase2 native minion summon and Zombie melee |
| Twilight Scepter bolt | CUSTOM_DAMAGE | 1 | Player Twilight Scepter |
| Naga ordinary melee with added push | VANILLA_LIKE_EXTENDED | 1 | Ordinary head melee |
| Naga charge block recoil/daze | CUSTOM_CONTROL | 2 | Native Player block during CHARGE |
| Naga stunless charge shield disruption | VANILLA_LIKE_EXTENDED | 2 | Native Player block during STUNLESS_CHARGE |
| Naga linked body routing/contact | VANILLA_LIKE_EXTENDED | 6 | Native segment contact with non-Animal Living |
| Naga source/home damage admission | BINARY_MECHANIC | 4 | Native incoming hit to head |
| Naga HP/body/speed and regeneration | CUSTOM_RESOURCE | 4 | Native incoming hit to head |
| Naga combat movement state machine | CUSTOM_CONTROL | 7 | Ordinary head melee |
| Naga combat terrain destruction/recovery | CUSTOM_CONTROL | 4 | Head adjacent terrain clearing |
| Axing melee and Minotaur axe sprint modifier | VANILLA_LIKE_EXTENDED | 11 | Native equipped Minoshroom ordinary melee |
| Ground slam damage and launch | CUSTOM_DAMAGE | 2 | Native GroundAttackGoal against grounded Players |
| Charge delivery and sprint state | CUSTOM_CONTROL | 8 | Native charge including a windup hit |
| Charge obstacle destruction | CUSTOM_CONTROL | 2 | Minoshroom native lava contact and accepted cleanup |
| Haunt melee and Knightmetal weapon predicates | VANILLA_LIKE_EXTENDED | 4 | Native numbered sword Knight melee |
| Thrown axe and pick lifecycle | CUSTOM_DAMAGE | 5 | Native axe Knight attack formation |
| Local formation and attack coordination | CUSTOM_CONTROL | 7 | Native axe Knight attack formation |
| Charging attack/armor/size tradeoff | VANILLA_LIKE_EXTENDED | 8 | Native numbered sword Knight melee |
| Timed guard and damage admission | BINARY_MECHANIC | 5 | Native thrown weapon hits Knight/owner/other entity or block |
| Formation flight and knockback | CUSTOM_CONTROL | 3 | Knight native lava contact and accepted cleanup |
| Multipart damage admission | BINARY_MECHANIC | 8 | Native hit on living open head |
| Head counters and regrowth | CUSTOM_RESOURCE | 6 | Native hit on living open head |
| Head attack scheduling | CUSTOM_CONTROL | 3 | Native head counter crossing and regrowth |
| Bite damage and blocking control | CUSTOM_DAMAGE | 2 | Native bite with blocking/nonblocking Player |
| Flame ray and ignition | CUSTOM_DAMAGE | 1 | Native flame ray and successful ignition |
| Mortar explosion and fire splash | CUSTOM_DAMAGE | 7 | Native nearby/distant owners and returned mortar |
| Body pressure and terrain clearing | CUSTOM_CONTROL | 1 | Native body/tail overlap and terrain pressure |
| Delayed HP recovery | CUSTOM_RESOURCE | 3 | Native root environmental and bypass damage |
| Three-fireball volley and lifecycle | VANILLA_LIKE_EXTENDED | 5 | Native three-shot Ur-Ghast volley |
| Damage-driven tantrum and admission | CUSTOM_RESOURCE | 6 | Native Player or timed shield reflection |
| Tantrum tear damage and minion lift | CUSTOM_DAMAGE | 2 | Native sky-exposed Player under tantrum box |
| Native minion summoning and targeting | CUSTOM_CONTROL | 7 | Native tantrum trap minion spawn |
| Nearby ghastling consumption and healing | VANILLA_LIKE_EXTENDED | 1 | Native minion/nonminion enters boss consumption box |
| Ghast trap charge and control | CUSTOM_CONTROL | 4 | Native ghastling deaths and redstone neighbor event |
| Trap-linked flight and target suppression | CUSTOM_CONTROL | 3 | Native flight path wrap replenishment |
| Projectile admission and native defenses | BINARY_MECHANIC | 5 | Native projectile-tagged hit before unlocking |
| Rampage, tired resource and native bomb scheduling | CUSTOM_RESOURCE | 6 | Native melee or environmental accepted unlock |
| Hostile grab, dismount and launch control | CUSTOM_CONTROL | 6 | Native Alpha Yeti grab attempt |
| Thrown-player native fall replacement | CUSTOM_DAMAGE | 5 | Native ordinary Yeti shared grab/throw/fall |
| Rampage landing slam | VANILLA_LIKE_EXTENDED | 2 | Native rampage fall area request |
| Falling ice damage and block lifecycle | CUSTOM_DAMAGE | 5 | Native random ceiling ice release |
| Rampage terrain and ceiling conversion | CUSTOM_CONTROL | 4 | Native full or interrupted rampage |
| Summon/drop/beam phase counters and admission | CUSTOM_RESOURCE | 6 | Native exposed Snow Queen body hit |
| Multipart ice-shield interception | BINARY_MECHANIC | 4 | Native normal attack on ice-shield part |
| Shield collision and phase-dependent melee | CUSTOM_DAMAGE | 3 | Native rotating shield contact in SUMMON/BEAM |
| Hover and counted drop control | CUSTOM_CONTROL | 3 | Native summon hover with clear/obstructed candidates |
| Order-dependent chilling-breath ray | CUSTOM_DAMAGE | 1 | Native chilling breath in BEAM hover |
| Independent Ice Crystal summon producer | CUSTOM_CONTROL | 5 | Native summon hover with clear/obstructed candidates |
| Ice Crystal melee, descent, melt and expiry | VANILLA_LIKE_EXTENDED | 4 | Native phase and minion save/load |
| Drop-phase terrain ice removal | CUSTOM_CONTROL | 1 | Native DROP ICE terrain destruction |
| Retaliation breath targeting and timing | CUSTOM_CONTROL | 3 | Native FireBeetle retaliation breath |
| Fire Beetle scorching and ignition | CUSTOM_DAMAGE | 3 | Native FireBeetle retaliation breath |
| Winter Wolf physical breath | VANILLA_LIKE_EXTENDED | 3 | Native WinterWolf retaliation breath |
| Nature Bolt damage, poison and terrain | CUSTOM_DAMAGE | 7 | Native Druid hoe bolt on Living victim |
| Druid equipment goals and permanent baby state | CUSTOM_CONTROL | 4 | Native Druid hoe bolt on Living victim |
| Tome Bolt alternating source and Slowness | CUSTOM_DAMAGE | 4 | Native off-lectern TomeBolt attack |
| Lectern ambush and release control | CUSTOM_CONTROL | 4 | Native generated lectern mimic gaze activation |
| Death Tome fire vulnerability | VANILLA_LIKE_EXTENDED | 2 | Native lectern removal or accepted hurt release |
| Slime Beetle throwable damage and disposal | VANILLA_LIKE_EXTENDED | 2 | Native SlimeBeetle shot and Living impact |
| Stable Ice Core snowball package | CUSTOM_DAMAGE | 3 | Native StableIceCore snowball impact |
| Unstable Ice Core delayed explosion | VANILLA_LIKE_EXTENDED | 2 | Native stable/unstable core descent, melting and melee |
| Unstable Ice Core terrain transmutation | CUSTOM_CONTROL | 2 | Native delayed UnstableIceCore explosion |
| Mist Wolf darkness-gated Blindness | VANILLA_LIKE_EXTENDED | 1 | Native MistWolf melee in darkness |
| Mounted goblin knight coupling | CUSTOM_CONTROL | 5 | Native Lower spawn and Upper passenger |
| Goblin knight shared shield resource | CUSTOM_RESOURCE | 8 | Native Lower spawn and Upper passenger |
| Directional goblin armor stripping | VANILLA_LIKE_EXTENDED | 5 | Native Lower spawn and Upper passenger |
| Timed heavy spear area attack | VANILLA_LIKE_EXTENDED | 3 | Native Lower delegated or solo melee |
| Pinch Beetle capture and carrying | CUSTOM_CONTROL | 3 | Native PinchBeetle charge capture and damage |
| Pinch Beetle clamped damage | CUSTOM_DAMAGE | 2 | Native PinchBeetle charge capture and damage |
| Pinch Beetle boat destruction on pickup | BINARY_MECHANIC | 1 | Native Boat collision pickup of PinchBeetle |
| Ordinary Yeti hurt-triggered persistent anger | CUSTOM_CONTROL | 3 | Native ordinary Yeti shared grab/throw/fall |
| Goblin melee with spike-part attribution | CUSTOM_DAMAGE | 1 | Native goblin ordinary melee |
| Goblin orbit/throw collision and control | VANILLA_LIKE_EXTENDED | 4 | Native goblin orbit contact |
| Goblin spike part damage rejection | BINARY_MECHANIC | 2 | Native spike part and root damage distinction |
| Chain Block launch, return and stack resource | CUSTOM_RESOURCE | 9 | Native mainhand BlockAndChain launch |
| Thrown Chain Block spiked damage | CUSTOM_DAMAGE | 6 | Native ChainBlock outbound/returning entity impact |
| Chain Block pre-hurt shield disruption | VANILLA_LIKE_EXTENDED | 2 | Native ChainBlock used-shield disruption |
| Destruction terrain smash and per-entity budgets | CUSTOM_RESOURCE | 3 | Native unenchanted/unbreakable block collision |
| Giant and Armored Giant native ant melee | CUSTOM_DAMAGE | 4 | Native GiantMiner equipped melee |
| Giant weapon attack and interaction attributes | VANILLA_LIKE_EXTENDED | 3 | Native Player GiantPick melee |
| Hedge and swarm spider native AI/defense inheritance | VANILLA_LIKE_EXTENDED | 4 | Native HedgeSpider melee/acquisition |
| King Spider rider composition and melee start gate | CUSTOM_CONTROL | 3 | Native King adult Druid producer |
| Swarm and Tower Broodling probabilistic melee admission | VANILLA_LIKE_EXTENDED | 5 | Native SwarmSpider probabilistic melee |
| Mosquito melee and native Hunger resource effect | VANILLA_COMPOSITE | 4 | Native Mosquito admitted hit and Hunger |
| Borer pre-admission reinforcement timer and block scan | CUSTOM_CONTROL | 4 | Native Borer causing-entity hurt schedules release |
| Borer conditional towerwood infestation and discard | CUSTOM_CONTROL | 2 | Native idle Borer towerwood merge |
| Infested towerwood native drop and explosion release | CUSTOM_CONTROL | 4 | Native Borer grief-admitted block scan |
| Redcap shyness and TNT avoidance | CUSTOM_CONTROL | 3 | Native finalized Redcap/Sapper melee and equipment |
| Redcap TNT ignition and Sapper finite planting | CUSTOM_CONTROL | 3 | Native Sapper finite TNT placement |
| Redcap and Sapper native TNT blast delivery | VANILLA_COMPOSITE | 6 | Native Redcap or Sapper existing TNT ignition |
| Kobold dropped-bread pickup and temporary pacification | CUSTOM_CONTROL | 5 | Native dropped bread search and pickup |
| Kobold local death-triggered panic | CUSTOM_CONTROL | 1 | Native same-class nearby death panic |
| Kobold small-flock center navigation | CUSTOM_CONTROL | 1 | Native small-group center navigation |
| Troll rock acquisition, combat task and saved state | CUSTOM_RESOURCE | 6 | Native Troll no-rock melee and sun avoidance |
| Troll block projectile ownerless damage | CUSTOM_DAMAGE | 5 | Native Troll ranged-goal new projectile |
| Carminite Golem admitted melee and vertical push | VANILLA_COMPOSITE | 2 | Native Carminite Golem successful melee |
| Maze Slime size and threefold native health | VANILLA_LIKE_EXTENDED | 5 | Native MazeSlime randomized finalization |
| Maze Slime tiny and NoAI contact admission | VANILLA_LIKE_EXTENDED | 6 | Native MazeSlime Player contact |
| Snow Guardian actual equipment and inherited ice behavior | VANILLA_COMPOSITE | 5 | Native SnowGuardian four equipment variants |
| Wraith native flight, home and attack scheduling | CUSTOM_CONTROL | 6 | Native Wraith two sequential melee requests |
| Rising Zombie gaze and native conversion | CUSTOM_CONTROL | 7 | Native RisingZombie nearest-player gaze trigger |
| Rising Zombie exact source immunity gate | BINARY_MECHANIC | 3 | Native RisingZombie in-wall source rejection |
| Zombie Scepter native owned summon | CUSTOM_CONTROL | 2 | Native Zombie Scepter owned summon |
| Loyal Zombie fixed attack and successful push | VANILLA_COMPOSITE | 1 | Native LoyalZombie melee |
| Loyal Zombie absent-Strength expiration | CUSTOM_DAMAGE | 3 | Native missing-Strength expiration |
| Owner flesh feed and effect/heal refresh | VANILLA_COMPOSITE | 1 | Native owner flesh interaction |
| Loyal Zombie owner response and follow | VANILLA_COMPOSITE | 3 | Native owner hurt/attack responses |
| Crown-produced persistent Loyal baby | VANILLA_LIKE_EXTENDED | 2 | Native Crown baby summon |
| Persistent scepter durability charges | CUSTOM_RESOURCE | 4 | Native Zombie Scepter owned summon |
| Renewal hand/inventory reagent recharge | CUSTOM_RESOURCE | 6 | Native Renewal hand ticks |
| Temporary and permanent Fortification shields | CUSTOM_RESOURCE | 8 | Native Fortification Scepter use |
| Fortification incoming damage cancellation | BINARY_MECHANIC | 2 | Native Fortification incoming hit |
| Lifedrain native selection and custom damage | CUSTOM_DAMAGE | 6 | Native Fortification incoming hit |
| Lifedrain low-health execution and bonus loot | BINARY_MECHANIC | 3 | Native nonboss low-HP nonPlayer execution |
| Lifedrain admitted slow and caster restoration | VANILLA_COMPOSITE | 3 | Native Lifedrain custom request |
| Lifedrain independent vertical motion replacement | CUSTOM_CONTROL | 1 | Native health-gated Lifedrain motion |
| Crown scepter charge-saving branch | CUSTOM_RESOURCE | 3 | Native Lifedrain durability and Crown |
| Moonworm zero-or-one native impact | CUSTOM_DAMAGE | 5 | Native Queen charged release |
| Moonworm bare-head forced equipment | BINARY_MECHANIC | 2 | Native bare-head impact |
| Moonworm charge and Torchberry repair | CUSTOM_RESOURCE | 3 | Native Queen charged release |
| Cube tracking, steering and return | CUSTOM_CONTROL | 6 | Native registered Cube item use |
| Cube fixed native melee-source hit and shield disable | VANILLA_LIKE_EXTENDED | 5 | Native Cube Living impact |
| Cube admitted terrain removal | BINARY_MECHANIC | 3 | Native Cube block removal |
| Ender impact position and vehicle swap | CUSTOM_CONTROL | 4 | Native Ender Player arrow impact |
| Seeker selection and velocity steering | CUSTOM_CONTROL | 5 | Native Seeker priority acquisition |
| Seeker native arrow damage and parent effects | VANILLA_LIKE_EXTENDED | 6 | Native Seeker plain arrow impact |
| Triple Bow native arrow fan and pre-spawn wear | VANILLA_LIKE_EXTENDED | 3 | Native Triple Player volley |
| Peacock Fan native entity and Player packet motion | CUSTOM_CONTROL | 3 | Native Fan entity motion |
| Peacock Fan aerial impulse and fall context | CUSTOM_CONTROL | 3 | Native airborne Fan boost |
| Dispenser Fan Living motion and wear gate | CUSTOM_CONTROL | 1 | Native dispenser Fan push |
| Native ignition with source-specific combat admission | VANILLA_LIKE_EXTENDED | 10 | Native Player Fiery Sword/Pick primary hit |
| Glass Sword native attack and two break paths | CUSTOM_RESOURCE | 3 | Native ordinary Glass Sword primary attack |
| Stale Bread native factory source replacement | CUSTOM_DAMAGE | 3 | Native Stale Bread Player melee/sweep |
| Knightmetal native shield and repair | VANILLA_DIRECT | 2 | Native Knightmetal Player shield block |
| Conventional Twilight tool and armor attributes | VANILLA_DIRECT | 3 | Native crafted conventional tools and armor |
| Arctic snow collision and Fiery/Arctic freeze eligibility | VANILLA_DIRECT | 2 | Native Arctic Boots snow surface collision |
| Charms of Life native death veto and restoration | BINARY_MECHANIC | 3 | Native LifeI inventory lethal hit |
| Travellers modifier registry, crafting and removal | CUSTOM_RESOURCE | 2 | Native registry/component save and reload |
| Travellers native loadout and equipment predicates | VANILLA_COMPOSITE | 4 | Native four main pieces equipped |
| Travellers last-durability and stored-attribute state | CUSTOM_RESOURCE | 6 | Native armor-wear threshold hit |
| Travellers native Auto-Repair probability | CUSTOM_RESOURCE | 4 | Native armor-hit delay tracking |
| Travellers Perfect Dodge impact veto | BINARY_MECHANIC | 2 | Native arrow impacts eligible vest wearer |
| Travellers missed-arrow native recovery | CUSTOM_RESOURCE | 2 | Native survival allowed-arrow block hit |
| Travellers All-Night native admission | BINARY_MECHANIC | 3 | Native per-player phantom spawn admission |
| Travellers crouch invisibility | VANILLA_LIKE_EXTENDED | 2 | Native crouching Stealth Player tick |
| Travellers passive native Haste | VANILLA_LIKE_EXTENDED | 1 | Native living wearer Haste tick |
| Travellers oxygen and submerged mining attributes | VANILLA_COMPOSITE | 2 | Native Aquatic goggles underwater air |
| Travellers movement and jump exhaustion reduction | CUSTOM_RESOURCE | 2 | Native transformed ServerPlayer movement |
| Travellers native water-surface collision | CUSTOM_CONTROL | 3 | Native source-water surface collision |
| Travellers terrain movement overrides | CUSTOM_CONTROL | 5 | Native block speed and jump factor overrides |
| Travellers native swim-efficiency attribute | VANILLA_DIRECT | 1 | Native Vest water travel |
| Travellers crouch-controlled step attribute | VANILLA_LIKE_EXTENDED | 1 | Native boots obstacle stepping |
| Travellers renewed native Jump Boost | VANILLA_LIKE_EXTENDED | 2 | Native Wings Jump Boost renewal |
| Travellers fall veto and stored bounce | CUSTOM_CONTROL | 5 | Native eligible fall event cancellation |
| Travellers descent and fall-distance control | CUSTOM_CONTROL | 4 | Native descending Player glide |
| Travellers stored second-jump availability | CUSTOM_CONTROL | 6 | Native JumpEvent and saved bounce boost |
| Travellers native sidestep impulse and cooldown | CUSTOM_CONTROL | 3 | Native on-ground left/right double tap |
| Travellers directional speed and FOV compensation | CUSTOM_CONTROL | 2 | Native server speed presence lifecycle |
| Travellers eligible item-use input recovery | CUSTOM_CONTROL | 2 | Native ProjectileWeapon item-use movement |
| Twilight native food nutrition and saturation | VANILLA_DIRECT | 14 | Native plain foods and jerky nutrition |
| Torchberry native Glowing | VANILLA_DIRECT | 1 | Native Torchberries consumption |
| Hydra Chop native Regeneration | VANILLA_DIRECT | 1 | Native Hydra Chop consumption |
| Meef Stroganoff native Fire Resistance and Strength | VANILLA_COMPOSITE | 1 | Native Meef Stroganoff consumption |
| Gelatinous Slime Drop native Speed | VANILLA_DIRECT | 1 | Native Slime Drop food effect |
| Gelatinous Maze Slime Drop native Resistance | VANILLA_DIRECT | 1 | Native Maze Slime Drop food effect |
| Twilight probabilistic berry duration extension | VANILLA_LIKE_EXTENDED | 5 | Native Blightberry independent regeneration/poison/wither |
| Brittle/Greater flask dose and breakage resource | CUSTOM_RESOURCE | 10 | Native flask in slot filled from cursor |
| Flask native potion effect delivery | VANILLA_COMPOSITE | 5 | Native Brittle flask use/breakage |
| Flask failed-challenge ownerless damage | CUSTOM_DAMAGE | 2 | Native Strong Harming FAILED_CHALLENGE |
| Experiment115 portion storage and regeneration | CUSTOM_RESOURCE | 5 | Native Experiment115 handheld food |
| Pocket Watch native inventory effects | VANILLA_COMPOSITE | 4 | Native Pocket Watch in hotbar |
| Pocket Watch Mining Fatigue application veto | BINARY_MECHANIC | 1 | Native held-watch Mining Fatigue application |
| Transformation Powder native entity replacement | CUSTOM_CONTROL | 5 | Native Player mapped-entity Powder interaction |
| Thorns regrowth and Burnt removal | CUSTOM_CONTROL | 7 | Native Lamp immediate clicked-thorn conversion |
| Timewood core native callback acceleration | CUSTOM_CONTROL | 4 | Native grower save/extra ticker |
| Deer feeding native healing | VANILLA_LIKE_EXTENDED | 3 | Native adult Deer breeding feed |
| Passive bird descent, flight and contact control | CUSTOM_CONTROL | 5 | Native Bird descent including Penguin |
| Passive native fall and freezing eligibility | VANILLA_DIRECT | 2 | Native passive fall immunity |
| Thorns ownerless contact damage | CUSTOM_DAMAGE | 3 | Native Brown/Green thorn overlap |
| Oreberry ownerless contact damage | CUSTOM_DAMAGE | 1 | Native Oreberry overlap all ages |
| Knightmetal ownerless contact damage | CUSTOM_DAMAGE | 2 | Native Knightmetal contact |
| Fiery Block native contact damage | CUSTOM_DAMAGE | 1 | Native Fiery step contact |
| Fiery Block native fire support and Strider warmth | VANILLA_COMPOSITE | 2 | Native fire supported by Fiery |
| Fire Jet native pulsed damage | CUSTOM_DAMAGE | 7 | Natural fuel-fed Fire Jet |
| Fire Jet independent native fire-timer assignment | VANILLA_LIKE_EXTENDED | 7 | Natural fuel-fed Fire Jet |
| Carminite Reactor latched terrain sequence | CUSTOM_CONTROL | 6 | Native six-redstone Reactor latch |
| Reactor ownerless native explosion and movement | CUSTOM_DAMAGE | 5 | Native six-redstone Reactor latch |
| Reactor native default Ghastling production | CUSTOM_RESOURCE | 4 | Native six-redstone Reactor latch |
| Reactor Debris temporary full collision | CUSTOM_CONTROL | 3 | Reactor native primary shell sequence |
| Slider native contact damage and independent knockback | CUSTOM_DAMAGE | 5 | Native stationary Slider contact |
| Slider native block-to-entity motion and restoration | CUSTOM_CONTROL | 7 | Native Slider scheduled connected-state admission |
| Ominous Fire native non-fire contact damage | CUSTOM_DAMAGE | 7 | Native Essence-created Ominous Fire |
| Ominous death native mapped entity replacement | CUSTOM_CONTROL | 3 | Native lethal Ominous Horse conversion |
| Ominous player death profile-bearing Zombie | CUSTOM_RESOURCE | 4 | Native lethal Ominous Horse conversion |
| Zombified-player incoming source wrapper and native re-entry | CUSTOM_DAMAGE | 2 | Native Zombie profile persistence and later melee |
| Acid Rain native biome damage | CUSTOM_DAMAGE | 3 | Native Highlands Acid Rain |
| Locked Dark Forest native Darkness | VANILLA_DIRECT | 3 | Native Highlands Acid Rain |
| Locked Swamp native Hunger stacking | VANILLA_LIKE_EXTENDED | 3 | Native Highlands Acid Rain |
| Progression structure hostile damage gate | BINARY_MECHANIC | 5 | Native unprotected Stronghold access and upper pieces |
| Progression native hint Kobold production | CUSTOM_RESOURCE | 4 | Native hint attempt from denied action/attack |
| Portal native lightning delivery modes | VANILLA_LIKE_EXTENDED | 7 | Native catalyst cost and write ordering |
| Cloud and Arctic Fur native fall multiplier | VANILLA_LIKE_EXTENDED | 1 | Native cloud fall callback |
| Cloud local rain eligibility and native consumers | VANILLA_LIKE_EXTENDED | 11 | Native installed local-rain ASM path |
| Native bound-zombie close-follow override | CUSTOM_CONTROL | 11 | Native leash close/elastic/break intervals |
| Multiplayer native spawn maximum-health adjustment | VANILLA_LIKE_EXTENDED | 3 | Native tagged boss base-spawner finalize |
| Hedge native cactus retaliation/contact | VANILLA_LIKE_EXTENDED | 4 | Hedge entityInside/stepOn |
| Maze slime inherited fall and motion | VANILLA_DIRECT | 3 | Maze slime landing fall request |
| Configured native encounter spawning | VANILLA_LIKE_EXTENDED | 2 | Lich room Sinister grounded native spawner |
| Hostile bookshelf native spawn and fire release | CUSTOM_CONTROL | 3 | Lich hostile bookshelf normal native tick |
| Controlled structure ambient encounter selection | CUSTOM_CONTROL | 2 | Native monster PotentialSpawns structure selection |
