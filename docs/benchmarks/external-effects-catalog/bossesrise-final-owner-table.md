# Bosses Rise combat owner table — COMPLETE

82 deduplicated combat packages; 232 native source/control/admission paths from 115 protected input packages. Static review only; no runtime tests.

Both custom DamageTypes are USED: cannonball_hit and kraken_tentacle_smash. All157 watched methods,18 native status references and6 source-key references have dispositions. Stage points identify future final native numeric requests only; production is unchanged.

| Mechanic | TNO classification | Single candidate Stage point / no-value reason |
|---|---|---|
| Dodge Roll native charges and recovery | CUSTOM_ROUTED, ADMISSION_GATED, NO_STAGE_VALUE | Fixed native resource/control/admission; no numeric HP/SHP payload to scale. |
| Dodge Roll native movement and control | CUSTOM_ROUTED, ADMISSION_GATED, NO_STAGE_VALUE | Fixed native resource/control/admission; no numeric HP/SHP payload to scale. |
| Dodge Roll damage/effect and explicit GlacialShove admission | CUSTOM_ROUTED, ADMISSION_GATED, NO_STAGE_VALUE | Fixed native resource/control/admission; no numeric HP/SHP payload to scale. |
| Dodge Roll native freeze-write veto | CUSTOM_ROUTED, ADMISSION_GATED, NO_STAGE_VALUE | Fixed native resource/control/admission; no numeric HP/SHP payload to scale. |
| Shared native boss damage | COMPOSITE, ADMISSION_GATED, VANILLA_ROUTED, NUMERIC_SCALABLE | Once at final target.hurt amount after damageScale * ATTACK_DAMAGE and EnchantmentHelper.modifyDamage. |
| Native boss lethal-hit choreography | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Native control/source/part/death choreography; no additional scalable amount. |
| Knight native spawn HP/control prerequisite | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Native control/source/part/death choreography; no additional scalable amount. |
| Native multipart damage forwarding | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Native control/source/part/death choreography; no additional scalable amount. |
| Native owner-aware summon targeting | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Native control/source/part/death choreography; no additional scalable amount. |
| Native raw additive combat displacement | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Native control/source/part/death choreography; no additional scalable amount. |
| Knight stack resource and hurt admission | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Native defense/resource/phase or incoming-attack modifier; no additional Stage multiplier. |
| Knight native weak-point mark forwarding | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Native defense/resource/phase or incoming-attack modifier; no additional Stage multiplier. |
| Knight native HP-triggered state gates | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Native defense/resource/phase or incoming-attack modifier; no additional Stage multiplier. |
| Knight cinematic/resurrection/revenge/death control | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Native defense/resource/phase or incoming-attack modifier; no additional Stage multiplier. |
| Knight native combat defenses and visibility | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Native defense/resource/phase or incoming-attack modifier; no additional Stage multiplier. |
| Knight native suffocation-typed ring damage | COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE | Once at final in_wall12 hurt; retain native iframe and geometry. |
| Native SwordWave attributed indirect magic | COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE | Once at final ceil(currentSpeed*baseDamage) indirect_magic hurt. |
| Native arrow HP with distinct real producers | COMPOSITE, ADMISSION_GATED, VANILLA_ROUTED, NUMERIC_SCALABLE | Once at final native AbstractArrow hurt after speed/base/critical/enchantment calculation, retaining each native projectile/weapon owner and eligibility. Do not also scale baseDamage or source equipment attributes. |
| SoulShockwave independent explosion-typed area damage | COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE | Once at each independent explicit explosion4 hurt, retaining native admission. |
| Rift native ownerless magic | COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE | Once at final ownerless magic2 hurt. |
| Native AI melee with explicit timer, range and LOS admission | COMPOSITE, ADMISSION_GATED, VANILLA_ROUTED, NUMERIC_SCALABLE | Once at inherited Mob.doHurtTarget final native mob_attack after attributes/enchantments. Keep anonymous canPerformAttack and separate timed hit admission. |
| Native animation-timed summon and guardian melee | COMPOSITE, ADMISSION_GATED, VANILLA_ROUTED, NUMERIC_SCALABLE | Once at each actual timed native mob_attack hurt using current attacker ATTACK_DAMAGE. Preserve own-source identity, per-class ranges/block gates and independent status/control; do not scale attribute too. |
| Native Wither damage tick | COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE | Once at native WitherMobEffect final wither1 hurt; no amplifier/duration multiplier. |
| Native Slowness application variants | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Native control/status/duration/admission/geometry or source prerequisite; no additional Stage value. |
| Native Rift emitter/homing/lifecycle | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Native control/status/duration/admission/geometry or source prerequisite; no additional Stage value. |
| Arena mob independent movement and defense | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Native control/status/duration/admission/geometry or source prerequisite; no additional Stage value. |
| Infernal Dragon phase/source admission | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Native admission, phase/resource or control; no independent outgoing HP amount. |
| Dragon cinematic effects and death control | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Native admission, phase/resource or control; no independent outgoing HP amount. |
| Dragon independent melee displacement | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Native admission, phase/resource or control; no independent outgoing HP amount. |
| Blazing Fireball independent impact hazard and ignition | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Native admission, phase/resource or control; no independent outgoing HP amount. |
| Native explosion HP with distinct producers and pass counts | COMPOSITE, ADMISSION_GATED, VANILLA_ROUTED, NUMERIC_SCALABLE | Once at each actual native Explosion.explode per-victim hurt after exposure/calculator, retaining native explosion/player_explosion source and the boots repeated-pass lifecycle; never scale radius or wrapper plus final amount. |
| Fire Area native contact damage | COMPOSITE, ADMISSION_GATED, VANILLA_ROUTED, NUMERIC_SCALABLE | FireAreaEntity.tick touchingEntity.hurt(inFire,1.5) final amount. |
| Dragon breath conditional magic | COMPOSITE, ADMISSION_GATED, VANILLA_ROUTED, NUMERIC_SCALABLE | InfernalDragonEntity lambda$spawnFireBreath$5 final magic2 or1.5 Player.hurt request. |
| Native fire block damage from Dragon paths | COMPOSITE, ADMISSION_GATED, VANILLA_ROUTED, NUMERIC_SCALABLE | BaseFireBlock.entityInside final inFire fireDamage request with proven native-origin attribution; no global unrelated-fire scaling. |
| Native burning from Dragon/Blazing paths | COMPOSITE, ADMISSION_GATED, VANILLA_ROUTED, NUMERIC_SCALABLE | Entity.baseTick final onFire1 hurt request with proven origin attribution, not ignition duration plus damage. |
| Guardian timed push and blocking-item cooldown | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Native admission, phase/resource or control; no independent outgoing HP amount. |
| Yeti native admission and projectile reductions | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Incoming native modifiers, admission/state/resources or scripted HP reset; no independent outgoing HP payload. |
| Yeti raw lethal death/corpse lifecycle | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Incoming native modifiers, admission/state/resources or scripted HP reset; no independent outgoing HP payload. |
| Yeti predicted HP enrage and ultimate resources | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Incoming native modifiers, admission/state/resources or scripted HP reset; no independent outgoing HP payload. |
| Yeti combat initialization, traits and persistence | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Incoming native modifiers, admission/state/resources or scripted HP reset; no independent outgoing HP payload. |
| Yeti independent iframe/freeze/motion controls | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Native binary/control/resource/geometry; no separate numeric HP payload. |
| Yeti native terrain-admitted ice creation | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Native binary/control/resource/geometry; no separate numeric HP payload. |
| Ice Spike native delayed freezing strike | COMPOSITE, ADMISSION_GATED, VANILLA_ROUTED, NUMERIC_SCALABLE | IceSpikeEntity lambda$baseTick final ownerless freeze stored-damage hurt argument. |
| Ice Cluster native delayed freezing strike | COMPOSITE, ADMISSION_GATED, VANILLA_ROUTED, NUMERIC_SCALABLE | IceSpikeClusterEntity lambda$baseTick final ownerless freeze stored-damage hurt argument. |
| Ice Cluster break/held/owner resource | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Native binary/control/resource/geometry; no separate numeric HP payload. |
| Yeti eligible freezing aura | COMPOSITE, ADMISSION_GATED, VANILLA_ROUTED, NUMERIC_SCALABLE | Shared attackEntity final explicit ownerless freeze amount after .225*attribute/native enchantment. |
| Ice Spike native swept magic hit | COMPOSITE, ADMISSION_GATED, VANILLA_ROUTED, NUMERIC_SCALABLE | IceSpikeProjectileEntity.onHitEntity final ceil/clamp speed*baseDamage hurt argument. |
| Ice Spike native playerTouch freezing hit | COMPOSITE, ADMISSION_GATED, VANILLA_ROUTED, NUMERIC_SCALABLE | IceSpikeProjectileEntity.playerTouch final explicit FREEZE 8 hurt argument. |
| Glacial Shove native pull/slow/attack control | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Native binary/control/resource/geometry; no separate numeric HP payload. |
| Native passive freezing from ice counters | COMPOSITE, ADMISSION_GATED, VANILLA_ROUTED, NUMERIC_SCALABLE | LivingEntity.aiStep final native freeze 1 hurt request with proven origin attribution, never counter and HP both. |
| Sandworm multipart damage and retaliation resource | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Native admission/resources, incoming modifier, scripted defeat, effect delivery or control; no additional scalable HP request here. |
| Sandworm native source, hidden and reload defenses | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Native admission/resources, incoming modifier, scripted defeat, effect delivery or control; no additional scalable HP request here. |
| Sandworm native phase and death sequence | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Native admission/resources, incoming modifier, scripted defeat, effect delivery or control; no additional scalable HP request here. |
| Sandworm passive part collision control | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Native admission/resources, incoming modifier, scripted defeat, effect delivery or control; no additional scalable HP request here. |
| Sandworm native sand column damage and push | COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE | SandColumn.damageEntity native hurt5 after eligibility and with its resolved magic/indirect_magic source; only once. |
| Sandworm poison applications and hazard admission | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Native admission/resources, incoming modifier, scripted defeat, effect delivery or control; no additional scalable HP request here. |
| Sandworm-origin native poison HP ticks | COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE | Native PoisonMobEffect hurt1 only with proven external-effect provenance and native HP>1 gate; no application/duration/amplifier scaling. |
| Sandworm native screech control | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Native admission/resources, incoming modifier, scripted defeat, effect delivery or control; no additional scalable HP request here. |
| Kraken body and tentacle native admission | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Native incoming modifier, resource/phase/admission, beneficial control or scripted cleanup; no separately scalable outgoing HP payload. |
| Kraken actual HP knockdown resource | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Native incoming modifier, resource/phase/admission, beneficial control or scripted cleanup; no separately scalable outgoing HP payload. |
| Kraken native tentacle phases and cinematic protection | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Native incoming modifier, resource/phase/admission, beneficial control or scripted cleanup; no separately scalable outgoing HP payload. |
| Kraken tentacle ownership, removal and respawn | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Native incoming modifier, resource/phase/admission, beneficial control or scripted cleanup; no separately scalable outgoing HP payload. |
| Kraken native death and scripted cleanup | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Native incoming modifier, resource/phase/admission, beneficial control or scripted cleanup; no separately scalable outgoing HP payload. |
| Kraken native tentacle smash and independent impulse | COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE | KrakenTentacle.attackEntityWithSlam final custom hurt after attribute/scale/clamp; do not scale separate impulse. |
| Kraken native thrown crate impact | COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE | ThrownCrate.onHitEntity ownerless magic2 native hurt only. |
| Kraken native runaway throw control | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Native control/admission/resources or prop durability; no additional scalable HP request here. |
| Native cannon rider ammunition and cooldown | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Native control/admission/resources or prop durability; no additional scalable HP request here. |
| Native cannon prop durability and tentacle delegation | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Native control/admission/resources or prop durability; no additional scalable HP request here. |
| Native cannonball custom impact | COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE | Cannonball.onHitEntity final custom cannonball_hit10 native hurt; no projectile speed scaling. |
| Pirate blocking item cooldown and raw impulse | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Native control/admission/resources or prop durability; no additional scalable HP request here. |
| Ice Gauntlet native use, freezing counter, leap and shard resources | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Native use/admission/control/resource or counter delivery; no additional outgoing HP multiplier here. |
| Ice Gauntlet native landing freezing pulse | COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE | GauntletAttachment.onFall native ownerless freeze10 hurt argument only; not frozen counter or delayed spike damage. |
| Sandworm Gauntlet native modes, cost and movement modifiers | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Native use/admission/control/resource or counter delivery; no additional outgoing HP multiplier here. |
| Undying Tentacle native entity/block pull | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Native control/admission/summon resource, ordinary inherited use or scripted lifetime; no additional scalable HP callback. |
| Undying Tentacle Ghost summon and lift resources | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Native control/admission/summon resource, ordinary inherited use or scripted lifetime; no additional scalable HP callback. |
| Ghost Tentacle control, ownership and lifetime | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Native control/admission/summon resource, ordinary inherited use or scripted lifetime; no additional scalable HP callback. |
| Kraken Trident native item and ownership lifecycle | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Native control/admission/summon resource, ordinary inherited use or scripted lifetime; no additional scalable HP callback. |
| Kraken Trident inherited direct hit | COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE | Inherited ThrownTrident.onHitEntity final native trident hurt after enchantment adjustment of8; no item attribute or speed scaling again. |
| Kraken Trident native area hit and independent pull | COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE | ThrownKrakenTrident.pullEntity final trident5 native hurt once; do not scale radius/control or re-scale inherited direct hit. |
| Dragon armor native buffs and equipment modifiers | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Native admission/control/resources/ordinary attributes, no additional HP scaling here. |
| Dragon armor native Post retaliation/ignition admission | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Native admission/control/resources/ordinary attributes, no additional HP scaling here. |
| Pirate Saber native owned summon delivery | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Native admission/control/resources/ordinary attributes, no additional HP scaling here. |

[Complete contracts](mod-reviews/block_factorys_bosses.json), [native paths and future fixtures](bossesrise-future-runtime-fixtures.json), [source coverage](bossesrise-total-source-coverage.json), [deduplication and additive correction map](bossesrise-final-promotion-map.json).

Compatibility priorities: Roll rejects damage/effects/frozen writes; boss phase/resources and direct-versus-causing predicates; native failed-hurt independent control/hazard callbacks; lost owner/save state; distinct active/passive freeze and native Poison eligibility; owned cannon splash uses player_explosion; boots explicitly repeat Explosion.explode and still invoke that pass after start cancellation. These are native static findings, not measured Tensura/L2 results.

Future integration review remains required:
- Future poison Stage integration requires an origin/merge policy and native HP>1 behavior review; no provenance implementation or runtime claim here.
- Future passive freeze/poison Stage requires proven origin and merge policy; no attribution bypass or production change.
- Future origin attribution for native fire ticks and shared explosion callbacks remains an integration decision; native source/admission must be preserved.
- Native boots bypass of ExplosionEvent.Start for explicit pass is documented only; no compatibility correction authorized.

Short exclusions: rendering/animation, ordinary attributes/melee, acquisition/food/repair, breakable decoration and structure/worldgen helpers without combat HP/status callbacks. Prior source-aid static-shoot wording is corrected in promoted contracts without rewriting history.

Exact next task: R2j1: Bosses of Mass Destruction installed-native combat source foundation, then bounded combat family review, on this same side-research branch. Continue automatically while quota is healthy under the existing user instruction. Eternal Starlight and Bosses Rise are complete; cross-mod R3 normalization/source minimization remains pending. No runtime boss matrix, L2, Stage, production, Phase6 reopening or Phase7.
