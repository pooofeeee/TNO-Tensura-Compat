# Ice & Fire combat owner table — COMPLETE

R2g10b promotes 81 combat packages and 228 native delivery/control/defense contracts. Installed-native static evidence only; all runtime fixtures remain unexecuted.

Gorgon conversion, ordinary HP damage, Poison, and statue destruction remain separate mechanics. Frozen/Siren accepted work is reused. Shared native ignition, Poison, Regeneration, lightning and arrow HP contracts are consolidated while retaining each native source path.

| Combat package | TNO category | Single Stage amount boundary / no-value reason |
|---|---|---|
| Frozen velocity control | CUSTOM_ROUTED, ADMISSION_GATED, NO_STAGE_VALUE | Velocity/lifecycle control; no HP payload or Stage amount. |
| Frozen weapon Slowness and Mining Fatigue | COMPOSITE, VANILLA_ROUTED, ADMISSION_GATED, NO_STAGE_VALUE | Independent native status requests; no duration/amplifier scaling. |
| Ice blood conditional native bonus | NUMERIC_SCALABLE, CUSTOM_ROUTED, ADMISSION_GATED | Once at DamageBonusAbility final target.hurt(bonusSource,bonus). |
| Dragon elemental HP requests | NUMERIC_SCALABLE, CUSTOM_ROUTED, ADMISSION_GATED | Each native target.hurt amount once in the downstream Stage amount layer; never also scale age/config, projectile and area. |
| Siren native song map and control | COMPOSITE, CUSTOM_ROUTED, ADMISSION_GATED, NO_STAGE_VALUE | Independent map-driven control and cosmetic status marker; no HP amount. |
| Siren Flute attachment pacification | CUSTOM_ROUTED, ADMISSION_GATED, NO_STAGE_VALUE | Binary target/navigation clearing over native timer; no HP amount. |
| Siren animated bite | NUMERIC_SCALABLE, VANILLA_ROUTED, ADMISSION_GATED | Once at Siren.aiStep victim.hurt(mob_attack,ATTACK_DAMAGE). |
| Siren animated pull and hit | COMPOSITE, NUMERIC_SCALABLE, CUSTOM_ROUTED, ADMISSION_GATED | Once at Siren.aiStep pull victim.hurt(mob_attack,ATTACK_DAMAGE); movement/rotation receive no multiplier. |
| Gorgon petrification | BINARY, CUSTOM_ROUTED, ADMISSION_GATED | Binary victim conversion/disposal with materially different player and non-player branches. The huge float is an execution proxy, not a scalable attack budget. |
| Gorgon fallback melee | NUMERIC_SCALABLE, VANILLA_ROUTED, ADMISSION_GATED | The amount delivered by native Mob.doHurtTarget to victim.hurt(mob_attack,amount), once in the normal damage pipeline. Do not also multiply ATTACK_DAMAGE or Gorgon animation. |
| Native Poison from Gorgon and Hydra | NUMERIC_SCALABLE, VANILLA_ROUTED, ADMISSION_GATED | Once at native PoisonMobEffect.applyEffectTick hurt amount, preserving HP>1 and effect admission. No duration/amplifier scaling; nonlethal behavior requires runtime/policy review before implementation. |
| Stone statue persistence and destruction | BINARY, CUSTOM_ROUTED, ADMISSION_GATED, NO_STAGE_VALUE | Persistent separate statue; positive projectile deletes; player pickaxe cracks threshold10; other damage delegates. |
| Native ignition and fire pulses | COMPOSITE, VANILLA_ROUTED, NUMERIC_SCALABLE, ADMISSION_GATED | Once at native Entity.baseTick on_fire hurt amount. Source-specific ignition seconds and admission remain unchanged; never add dragon or attacker attribution. |
| Dragon Lightning area control | CUSTOM_ROUTED, ADMISSION_GATED, NO_STAGE_VALUE | Native .3/.9 knockback is control and retains event/resistance rules; no additional TNO damage multiplier. |
| Optional dragon charge explosion | NUMERIC_SCALABLE, COMPOSITE, ADMISSION_GATED | Inherited Explosion.explode -> entity.hurt(calculator amount) once; preserve explicit manager source. Never scale explosion radius and damage amount together. |
| Dragon-placed vanilla fire contact | VANILLA_ROUTED, NUMERIC_SCALABLE | Existing BaseFireBlock.entityInside -> hurt(in_fire,fireDamage) once; delayed on_fire pulse belongs to ignition package, not another copy. |
| Dragon Ice Spikes contact | COMPOSITE, VANILLA_ROUTED, ADMISSION_GATED, NUMERIC_SCALABLE | IceSpikes.stepOn -> hurt(cactus,1) amount once after native/compat admission. Leave .5 knockback and placement frequency unchanged. |
| Dragon body/rider damage | NUMERIC_SCALABLE, VANILLA_ROUTED, ADMISSION_GATED | At target.hurt amount emitted by IafDragonLogic.attackTarget once (bite/tail/wing/tackle/rider). For shake, native updatePreyInMouth hurt amount once. Same downstream Stage layer, no attribute/animation/part second multiplication. |
| Dragon grab and body control | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | No extra numeric Stage value for mount/position/dismount or native tail/wing knockback; preserve hooks and independent hurt returns. |
| Dragon roar Strength/Weakness | VANILLA_ROUTED, ADMISSION_GATED, NO_STAGE_VALUE | Leave vanilla effect amplifier/duration/range intact; downstream native attacks already read modified attributes and receive Stage once. |
| Dragon combat healing and food restoration | NUMERIC_SCALABLE, COMPOSITE, ADMISSION_GATED | Heal requests: the one Dragon heal(amount) invocation through native LivingHealEvent. Direct food: only the HP delta at its native setHealth boundary, before native maxHP clamp; never multiply absolute current/maxHP or a paired damage event. Bite uses raw requested native damage for its heal formula, not observed HP loss. |
| Dragon native damage/corpse defenses | BINARY, ADMISSION_GATED, NO_STAGE_VALUE | Preserve all source/controller/parent/model gates and lightning message-id admission; never scale boolean rejection. |
| Dragon age/armor/hunger baselines | CUSTOM_ROUTED, NO_STAGE_VALUE | Native age, health/armor baselines, gear modifier and hunger counters stay native. Numeric attack/heal integration is already assigned elsewhere exactly once. |
| Dragon multipart damage routing | CUSTOM_ROUTED, ADMISSION_GATED, NO_STAGE_VALUE | No extra part multiplier beyond native partMultiplier. Apply any ordinary Stage amount once to resolved parent damage; native network/player paths require event-count validation. |
| Cockatrice and Scepter Wither damage | NUMERIC_SCALABLE, VANILLA_ROUTED, ADMISSION_GATED | Once at each native target.hurt amount: explicit Cockatrice strength-1 pulse, Scepter2 pulse, or vanilla Wither1 tick. Preserve ownerless attribution; do not also multiply status amplifier/duration. |
| Cockatrice gaze debuffs and pounce motion | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Native Slowness/Nausea, gaze and horizontal displacement stay native. |
| Cockatrice bite/pounce HP damage | NUMERIC_SCALABLE, VANILLA_ROUTED, ADMISSION_GATED | Native aiStep target.hurt amount once, after native attribute selection and before damage admission. |
| Combat gaze taming/allegiance | BINARY, CUSTOM_ROUTED, ADMISSION_GATED, NO_STAGE_VALUE | Taming threshold is native progress, not HP damage. |
| Cockatrice petrification immunity and incoming susceptibility | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Keep incoming native x5 and cached inWall veto; generic incoming Stage layer already owns damage. |
| Cockatrice native heal8 | NUMERIC_SCALABLE, VANILLA_ROUTED, ADMISSION_GATED | Once at native heal(8) request through LivingHealEvent, retaining HP clamp and consumption order. |
| Scepter native lock and shared durability budget | CUSTOM_ROUTED, ADMISSION_GATED, NO_STAGE_VALUE | Preserve UUID admission/lifecycle and cost; damage already assigned separately. |
| Death Worm/Cyclops native body HP damage | NUMERIC_SCALABLE, VANILLA_ROUTED, ADMISSION_GATED | Once at each native target.hurt amount (worm aiStep/tick, Cyclops aiStep/positionRider), after native attribute/config selection. |
| Death Worm attack and TNT explosions | NUMERIC_SCALABLE, VANILLA_ROUTED, ADMISSION_GATED | Once at inherited Explosion target.hurt final damage amount after native radius/visibility formula; never multiply radius or source creation. |
| Cyclops grab/kick displacement | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Native mount/position/knockback/dismount and independent HP result. |
| Cyclops arrow-eye blinding and native vulnerability | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Keep binary blindness/native x3; ordinary parent damage receives Stage once after native x3, no extra part scaling. |
| Death Worm immunity and multipart routing | BINARY, ADMISSION_GATED, NO_STAGE_VALUE | Keep native source/controller/statue exclusions and multiplier1 parent routing. |
| Tame Death Worm kill heal14 | NUMERIC_SCALABLE, VANILLA_ROUTED, ADMISSION_GATED | Once at killedEntity heal(14) amount through native LivingHealEvent. |
| Death Worm age/size HP reset | CUSTOM_ROUTED, NO_STAGE_VALUE | Native growth/reload baselines; never multiply absolute maxHP reset. |
| Held Cyclops Eye Weakness aura | VANILLA_ROUTED, ADMISSION_GATED, NO_STAGE_VALUE | Vanilla Weakness modifies native attacks; no extra multiplier on amplifier/duration/counter. |
| Ghost/Troll melee and native swords | NUMERIC_SCALABLE, VANILLA_ROUTED, ADMISSION_GATED | Once at native target.hurt request after native attack attribute/enchantment calculation; Ghost inherited Mob, Troll aiStep, sword ordinary Player attack. |
| Ghost Sword magic projectile damage | NUMERIC_SCALABLE, VANILLA_ROUTED, ADMISSION_GATED | Once at GhostSword.onHitEntity hurt amount after native speed/ceil/crit formula, not at both summed weapon modifier/baseDamage and impact. |
| Ghost Sword native impact control/fire/lifecycle | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Ignition native timer; generic on_fire damage only once downstream. Preserve hurt-success push and failure bounce; no synthetic projectile hook. |
| Ghost phasing, effect immunity and daytime inactivity | BINARY, ADMISSION_GATED, NO_STAGE_VALUE | Activity and native source/effect gates are not damage amounts. |
| Troll weapon explosion HP damage | NUMERIC_SCALABLE, VANILLA_ROUTED, ADMISSION_GATED | Once at inherited Explosion final target.hurt amount, not radius/visibility/source. |
| Troll strike motion, arrow veto and sunlight statue conversion | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Native fixed velocity, msgId veto and binary replacement remain native. |
| Native Regeneration from Troll and Hydra sources | NUMERIC_SCALABLE, VANILLA_ROUTED, ADMISSION_GATED | Once at native RegenerationMobEffect heal(1) request through LivingHealEvent. Do not scale duration/amplifier. |
| Troll/Dragon armor installed absorption hook | CUSTOM_ROUTED, ADMISSION_GATED, NO_STAGE_VALUE | Never scale this remaining-absorption expression. Intended HP mitigation is not proven in installed loader; test native composition first. |
| Hydra/Sea Serpent body and breath HP damage | NUMERIC_SCALABLE, VANILLA_ROUTED, ADMISSION_GATED | Once at native target.hurt amount in Hydra aiStep/Breath.onHit and Serpent hurtMob/doSplashDamage/Bubble.onHit, after native attribute selection. |
| Hydra head resource/regrowth/low-HP protection | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Keep native head budget and HP damage separate; no counter/threshold/zero-amount bypass or secondary Stage. |
| Inherited arrow HP damage with source-specific payloads | NUMERIC_SCALABLE, VANILLA_ROUTED, ADMISSION_GATED | Once at AbstractArrow.onHitEntity final hurt amount after native speed, base damage, crit and enchantments. Preserve separate accepted-hit poison/heal/control/shield effects; do not also scale baseDamage. |
| Hydra Arrow owner heal | NUMERIC_SCALABLE, VANILLA_ROUTED, ADMISSION_GATED | Once at doPostHurtEffects owner.heal(baseDamage) request, through native HealEvent. |
| Hydra shield wear/knockback and Serpent splash/boat removal | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Native control/resource cost independent of HP where code says so. |
| Serpent native source defenses, parts and lifecycle heal | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Keep native identity predicates and age/scale initialization; no repeated Stage at part or maxHP refresh. |
| Sea Serpent armor WaterBreathing/Strength | VANILLA_ROUTED, ADMISSION_GATED, NO_STAGE_VALUE | Native buffs modify underlying behavior; ordinary attack damage scaled downstream once. |
| Avian and mount native HP attacks | NUMERIC_SCALABLE, VANILLA_ROUTED, ADMISSION_GATED | Once at native hurt amount in Bird/Hippogryph aiStep or Amphithere tick/positionRider, rider tick, ordinary Player sword attack. |
| Native gust/scratch/attack motion | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Keep actual actor/target motion and native hurt-gated arrow/item versus independent creature control. |
| Victor, taming, rider protection and forced landing | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Native allegiance/control/immunity state, not numeric Stage amount. |
| Mount native healing | NUMERIC_SCALABLE, VANILLA_ROUTED, ADMISSION_GATED | Once at native heal(1/4/5) request through LivingHealEvent, retain native food/random/HP gates. |
| Hippocampus rider WaterBreathing | VANILLA_ROUTED, ADMISSION_GATED, NO_STAGE_VALUE | Native breathing status, no damage/Stage numeric value. |
| Dread native melee HP damage | NUMERIC_SCALABLE, VANILLA_ROUTED, ADMISSION_GATED | Once at final native hurt amount in animated aiStep or inherited Mob.doHurtTarget. |
| Dread animated attack knockback | VANILLA_ROUTED, ADMISSION_GATED, NO_STAGE_VALUE | Fixed native knockback independent of hurt result; retain resistance hook. |
| Lich summon and commander resource | COMPOSITE, CUSTOM_ROUTED, ADMISSION_GATED, NO_STAGE_VALUE | Preserve count/cooldown and actual commander resolution, no Stage multiplier. |
| Dread skull HP damage and homing | NUMERIC_SCALABLE, VANILLA_ROUTED, ADMISSION_GATED | Once at inherited AbstractArrow final hurt amount after speed/base/crit calculation. |
| Dread skull extra shield wear | VANILLA_ROUTED, ADMISSION_GATED, NO_STAGE_VALUE | Durability resource uses baseDamage, not HP amount; keep native7 default. |
| Dread tags, allegiance, immunity and mounting | BINARY, ADMISSION_GATED, NO_STAGE_VALUE | Preserve native and Tensura admission. No Stage on tags, owner, mount or immunity. |
| Real vanilla lightning from weapons and food | NUMERIC_SCALABLE, VANILLA_ROUTED, ADMISSION_GATED | Once at native Entity.thunderHit final lightning_bolt hurt amount after native/NeoForge admission. Do not scale bolt count or duplicate this at the summoner. |
| Dragonsteel visual-lightning mob_attack chain | NUMERIC_SCALABLE, VANILLA_ROUTED, ADMISSION_GATED | Once per final LightningMultihitAbility hurt; keep unscaled native queue amounts. |
| Additional sweep and gauntlet HP | NUMERIC_SCALABLE, VANILLA_ROUTED, ADMISSION_GATED | Once at custom sweep/gauntlet native player_attack hurt. |
| Slapper statuses and weapon knockback | COMPOSITE, VANILLA_ROUTED, ADMISSION_GATED, NO_STAGE_VALUE | Native status/knockback quantities unchanged. |
| Tide thrown and spin HP | NUMERIC_SCALABLE, VANILLA_ROUTED, ADMISSION_GATED | Once at TideTrident.onHitEntity final hurt for throw, or Player.attack final hurt for Riptide. |
| Persistent chain attachment and pull | COMPOSITE, CUSTOM_ROUTED, ADMISSION_GATED, NO_STAGE_VALUE | Direct movement/persistent UUID mechanics; no HP scalar. |
| Flute native flight interruption | BINARY, CUSTOM_ROUTED, ADMISSION_GATED, NO_STAGE_VALUE | Native recipient/owner/fallen state only. |
| Pixie native indirect_magic HP | NUMERIC_SCALABLE, VANILLA_ROUTED, ADMISSION_GATED | Once at PixieCharge.onHit native hurt5. |
| Pixie statuses, theft and hurt admission | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Statuses/item transfer and true-without-HP gate remain native. |
| Native Pixie healing | NUMERIC_SCALABLE, VANILLA_ROUTED, ADMISSION_GATED | Once at native Pixie heal5 request. |
| Combat food status support | COMPOSITE, VANILLA_ROUTED, ADMISSION_GATED, NO_STAGE_VALUE | Keep vanilla potion/nutrition/absorption resource quantities; downstream attacks scale once. |
| Full Lightning Dragonsteel native bolt immunity | BINARY, VANILLA_ROUTED, ADMISSION_GATED, NO_STAGE_VALUE | Exact damage type and four-slot IncomingDamage cancellation. |
| Conditional Ghost summon on Player death | BINARY, CUSTOM_ROUTED, ADMISSION_GATED, NO_STAGE_VALUE | Configured native summon; reuse Ghost attack Stage point. |
| Equipped Blindfold native Blindness | VANILLA_ROUTED, ADMISSION_GATED, NO_STAGE_VALUE | Native status and separate item-tag gaze admission, no HP scalar. |
| Native egg zero-amount impact | VANILLA_ROUTED, ADMISSION_GATED, NO_STAGE_VALUE | Zero native HP request must remain zero, hatching is separate. |
| Native creature targeting and fear navigation | BINARY, ADMISSION_GATED, NO_STAGE_VALUE | AI targeting/movement, no damage or Tensura fear status. |

## Runtime priorities

- Gorgon gaze versus Head; Player versus nonplayer; accepted/rejected lethal hurt and statue ordering; blindfold/LOS/native compat admission.
- ColdNullification versus Frozen companion effects; Siren map control versus marker immunity; attachment Post tick versus passenger ticks.
- Dragon source holder/direct/causing identity, especially ridden Lightning manager using ICE; independent direct/area/status/explosion attempts and native Tamable collision guard.
- Sea Serpent live-owner bubble gate and Dread Lich skull origin must be observed through genuine native AI; absence is not permission to inject a payload.
- Installed Uranus armor amount callback targets Player absorption. Lightning Dragonsteel cancellation uses a separate functioning Architectury incoming-damage hook.
- Ordinary versus custom weapon/arrow factories, real bolt versus cosmetic chain, accepted-hit payload gates, native resource persistence and whole-pack event cancellation.

[Every native path and preserved fixture](iceandfire-future-runtime-fixtures.json); [total promotion mapping](iceandfire-final-promotion-map.json); [accepted mechanic contracts](mod-reviews/iceandfire.json).

Short exclusions: ordinary crafting/acquisition, worldgen setup, utility/storage/transport without combat callbacks, cosmetics/rendering/animation-only branches. Dormant Dread necromancy and unregistered Queen are explicitly excluded as active native deliveries; Myrmex implementation is absent in this installed artifact.

Validation: deterministic promotion, bytecode/reference witnesses, all five accepted views, exact preservation of prior accepted mods and historical research, five tooling tests, Git scope/diff checks. No runtime, L2, Stage, production, Phase6 or Phase7 changes.

Exact next task: R2h1: Eternal Starlight installed-native combat source foundation. Reuse broad source aids, pin native registries/damage/status producers and direct compat; no repeated Ice & Fire, runtime, L2, Stage or production work.
