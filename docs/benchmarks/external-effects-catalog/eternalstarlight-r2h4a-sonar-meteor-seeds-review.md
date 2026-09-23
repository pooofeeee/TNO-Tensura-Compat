# R2h4a — Eternal Starlight sonar, meteor and seeds

Three native custom types plus distinct native Sonar Bomb and their actual item/mob/environment/armor deliveries; static only.

Static subsection complete. Runtime fixtures remain unexecuted; no Stage or production implementation.

## Sonar

Only combat source caller of custom SONAR is CrystallizedMothAttackGoal.tick. Native target-present/attackTicks0/random1-in50 starts; continues while attackTicks<100, increments each tick, then attackTicks>15 && hasLineOfSight(target) && distance<30 attempts hurt every tick. Amount=current ATTACK_DAMAGE (default and config snapshot1.5)*4 for #vulnerable_to_sonar_bomb else1; tag installed members Bat and Warden. Direct=causing=Moth, not its tame owner; no iframe reset, hurt return ignored. SONAR bypasses shields and has no_impact/no_knockback; armor/enchantments/Resistance/cooldowns still apply. The sonic visual cadence is not damage cadence and this is not vanilla sonic_boom.

## Moth admission

CrystallizedMoth.hurt unconditionally rejects exact SONAR before super, with no bypass-tag exception. Native target goals include owner hurt-by/hurt-target, retaliation and Bat prey. wantsToAttack failed source decompilation was resolved with pinned javap: rejects Creeper/Ghast, same-owner tame Moth, Player prohibited by Player-owner PvP, tamed horse, and other tamed TamableAnimal; another-owner tame Moth takes its earlier Moth branch and is allowed by this predicate. These are target-selection rules, not a new per-tick damage filter. checkFallDamage empty suppresses ordinary fall-processing path. Tame damaged Moth fed accepted food consumes one then heal(2*nutrition), or2 if no food component; not restricted to owner in that branch. Scale actual heal request once, leave food/target/SONAR-immunity binary rules native. Taming, breeding, gel production and cosmetics are otherwise excluded.

## Sonar bomb

Native Player throw speed1.5/cooldown20 and registered dispenser ownerless asProjectile are both legitimate. Server non-MISS impact inherited dispatch then all Living in projectile AABB inflated20 (cube, no LOS/radial/exposure test), shouldHarm(owner,victim), requests native damageSources.mobProjectile(this,Living owner or null), amount20 for the same Bat/Warden tag else5. Direct=bomb, causing=Living owner/null; hurt return ignored, no iframe reset, no Level.explode and no control/status effect despite explosion visuals. It does NOT create custom SONAR, so Moth SONAR immunity and that custom shield bypass do not apply. Native mob_projectile is projectile-routed with ordinary shield/armor/Resistance/protection. Preserve source tags/ownership rather than relabel as sonic damage.

## Meteor payload

AethersentMeteor onHit requires non-MISS, then natural OR (target absent AND targetPos absent) OR (target present AND meteorY<=targetY+targetHeight) OR (targetPos present AND meteorY<=targetPosY+1). For admitted server impact, Living candidates are meteor AABB inflated size in X/Z only; shouldHarm(owner,victim); set invulnerableTime=0 with no restore; custom METEOR hurt size*5*(Living owner?.08:1)*(Player owner?config.playerAethersentMeteorDamageScale:1). getEntityDamageSource receives OWNER, so direct=causing=owner, both null for natural ownerless, not projectile direct identity. Hurt return ignored; manual AoE, no explosion/exposure/LOS test. Natural size10 requests50; legitimate showers size2..4 request.8..1.6 with Living owner before Player config (default/snapshot1). METEOR tags do not confer projectile/explosion/fire or armor/shield/Resistance/protection bypass. Each independently requested victim hit gets Stage once after the complete native formula; do not scale size, spawn count or owner factor.

## Meteor producers

createMeteorShower server only, owner METEOR_COOLDOWN>0 returns; otherwise stores caller cooldown then nine owned meteors (3x3 jitter), random size2..4, natural=false, target reference and original targetPos. Tick sets downward velocity -4 (natural -2) after super tick; no X/Z homing. RageOfStars successful item callback or native swing-packet path performs entity-only ray20 (nonspectator Living; no block clip/ally filter); uses found target or point10 ahead, height30,cooldown60. StarfallLongbow marks its native arrow; impact handler server plus Living owner clears marker FIRST and requests shower at hit position, Living target if applicable, height30,cooldown60, independent of subsequent primary arrow hurt. No native Starfall firework producer is proven. Armor counterattack is LivingDamageEvent.Post, attribute chance check and Living causing attacker -> victim-owned shower targeting attacker height30,cooldown120; no amount>0 test here. Aethersent armor adds.25 chance per matching slot, attribute range0..1; ordinary source-less hits cannot counter. Owner shared cooldown decrements on server entity ticks, linking all these routes; no Stage on chance/cooldown/marker.

## Natural meteor and persistence

Starlight ServerLevelMixin tickPrecipitation RETURN -> active weather.tickBlock -> MeteorShowerWeather configured chance creates ownerless natural size10 meteor at terrain position+200Y. This is a real environmental combat path, not excluded worldgen. Native meteor hurt alwaysfalse/nonpickable; no ordinary destruction via HP. dropAndDiscard(false) after impact may independently spawn persistent Creteor only for natural size>=10 with enabled/chance/no existing Creteor within32; this is not hurt-success gated. Block replacement/loot are excluded as noncombat. Meteor save/load overrides omit super projectile methods: target/position/size/natural save, inherited owner is not written/restored by these overrides; reload can therefore change source ownership, .08 factor and shouldHarm eligibility. Preserve and test this behavior, do not repair it here. Weather also spawns TinyCreteors; their creature attacks remain for the creature closure section.

## Seeds delivery

SeedsLauncher Player use requires nonempty chosen projectile and nonempty native draw. Base count6 goes through EnchantmentHelper.processProjectileCount; native useAmmo consumes first ammo and uses a copy for subsequent entries. Server shoots owned ShotSeeds speed.75*ammo speedMultiplier, inaccuracy7.5; one weapon durability request, player cooldown=int(ammo.cooldown*20). #seeds_launcher_ammo accepts #c:seeds; data registry lookup matches item, else wheat fallback, missing wheat throws. Eight installed ammo tuples damage/speed/cooldownSeconds: wheat1/1/1, torchflower1.5/1/1.2, beetroot.8/1.2/.8, melon1.2/.9/1.1, pumpkin.4/1.5/.5, crinoa1.2/1/1, nocturnal_millet1.5/1.5/.8, pungency_fruit1.5/.9/1.2. Stranghoul has real RangedAttackGoal interval30/range5 and mainhand launcher predicate; performRangedAttack further requires target intersect AABB inflated6, then same launcher method. Native mob getProjectile held supported ammo else PungencyFruitSeeds; it does not call Player item-use cooldown. No ShotSeeds dispenser producer proven.

## Seeds payload

ShotSeeds carries copied fired weapon and native projectile-spawn enchant callbacks. Entity impact base.5 -> modifyDamage(server,weapon,target,customSEEDS,base) if weapon available -> add speed magnitude*1.25 -> multiply ammo damageMultiplier -> target invulnerableTime=0 without restore -> hurt. Direct=seed projectile, causing=owner. Hurt true gates enchantment post effects for Living server target and, independently of Living type, ignition if seed on fire: remainingFireTicks/20/15 seconds. Hurt false skips both; onHit discards regardless. No shouldHarm/ally check added in this override; inherited projectile collision eligibility remains, so test allied collateral through genuine delivery. SEEDS is IS_PROJECTILE but has no armor/shield/Resistance/protection/cooldown bypass tag (cooldown reset is explicit code). Tick super first, age>40 if burning else>80 discards, then water/rain/powder snow clears fire. Custom firedFromWeapon has no save/load methods, so reload retains inherited projectile state but loses that copied weapon/enchantment basis. Scale only final SEEDS hurt after enchant+speed+ammo, not speed/count/partial formula; ensuing native fire DOT retains its own existing vanilla processing.

## Boundaries

All three custom types are USED with concrete callers. Native damage-source identity and native difficulty scaling remain; no Tensura SHP effect or successful L2 compatibility is inferred. Runtime fixtures are pending. Seed resources, fire duration, meteor cooldown/chance/count/size, sonar cadence and targeting are not multiplied by Stage. The ordinary sword/arrow primary hits use their existing vanilla damage path independently of these secondary payloads; never multiply both a shared attribute and the final request. No permanent integration change is authorized.

## TNO integration decisions

- **Crystallized Moth sonar**: COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE. Stage: Once at final SONAR hurt after attack attribute and vulnerability factor.
- **Moth sonar immunity and fall processing**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: no additional multiplier; Keep targeting, cooldowns, sources and native state unscaled.
- **Moth native feeding heal**: COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE. Stage: Once at native heal(2*nutrition or2).
- **Sonar Bomb native mob-projectile AoE**: COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE. Stage: Once at per-victim mobProjectile hurt, after vulnerability amount20/5 choice.
- **Aethersent Meteor manual area damage**: COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE. Stage: Once at final METEOR hurt after size/owner/config formula.
- **Meteor armor chance and shared owner cooldown**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: no additional multiplier; Keep targeting, cooldowns, sources and native state unscaled.
- **Meteor projectile damage rejection**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: no additional multiplier; Keep targeting, cooldowns, sources and native state unscaled.
- **Seeds Launcher pellet damage and ignition gate**: COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE. Stage: Once at final SEEDS hurt after enchantments plus speed, then ammo multiplier.

[Machine-readable packages, delivery paths and future fixtures](eternalstarlight-r2h4a-sonar-meteor-seeds.json). Exact archive/method witnesses and targeted semantic assertions are reproducible. No whole-mod completion claim.

Exact next task: R2h4b: Ether/Thioquartz, Shattered Blade and Wilt custom damage payloads and legitimate deliveries; then remaining ES equipment/spells/resources/mob defenses, dedup/promotion/full validation. Bosses Rise follows whole-ES completion while quota healthy.
