# R2h8a — Eternal Starlight combat closure

Final combat-significant source/admission gaps and brief noncombat exclusions; promotion remains next.

Static subsection complete. Runtime fixtures remain unexecuted; no Stage or production implementation.

## Coverage

Whole installed artifact inventory1384 classes;274 watched common/server combat/admission methods now have native method witnesses. All29 custom source-factory caller methods,31 damage-key references and38 custom-status reference methods remain protected in R2h1; all18 actual DamageTypes have reviewed caller families. Scans index semantic contracts and explicit exclusions, not proof that any witnessed class is automatically reviewed. Registries, nine effects, combat items/armor, creatures, AI, native projectiles, spells/crests, event bridges, mixins, environment and inherited hazard paths are accounted for. Full source disposition/promotion map is next, no runtime compatibility certification.

## Dusk

Server lit Dusk Light/Emitter activated face casts30block COLLIDER ray from face+.51; explicit always-passable tag wins, then always-unpassable tag, else HalfTransparentBlock passes. Beam stops at native hit, can activate receptor for5ticks and destroy tagged blocks. In beam AABB (transverse halfwidth.25), every Entity except ItemEntity gets setRemainingFireTicks(max(old,100)); no hurt, shouldHarm, owner or fireImmune test at writer. Emitter alwaysActivated refreshes5; ordinary/reinforced Light require receptor activation and FACING. Native Entity.baseTick fireImmune reduces timer4 without on_fire hurt; otherwise every20ticks when not lava requests ownerless on_fire1. Fire Resistance/native mitigation still matters. Scale only that final native fire hurt, never timer/range, and do not attribute beam to placer.

## Alloy

Server AlloyFurnace tick increments overheat while lit and either no cooling or litTicks%coolingEfficiency==0; unlit subtracts1 plus coolingEfficiency if cooling, clamp0..configured totalOverheatTicks. At threshold destroys furnace then Level.explode(null,null,null,center,configured explosionRadius,true,BLOCK,...). Native source factory yields ownerless explosion, no Player placer ownership, no custom ES type. Real damage/exposure/block admission and explosion events remain native. Radius/fuse/cooling and fire creation unscaled; each final native per-victim explosion hurt is sole Stage point, later placed fire keeps native fire scaling separately. Crafting/recipe/container details excluded.

## Inherited hazards

Three actual vanilla MagmaBlock instances (Abyssal/Thermabyssal/Cryobyssal) inherit stepOn: Living and !isSteppingCarefully -> ownerless hot_floor1. No extra Frost Walker predicate in installed method; native downstream admission remains. TorreyaCampfire constructor damage1 inherits lit Living contact campfire1 independently of its already-reviewed status aura. No ice/cold source inferred from Cryobyssal name. Scale each final native hot_floor/campfire hurt once; reuse existing contact/fall packages on promotion where identical.

## Native movement

LunarisCactusGelBlock extends SlimeBlock: nonsuppressed bounce fall multiplier0, reflectedY*1 Living/.8 other; careful/suppressed bounce delegates ordinary fall, low-|Y|<.1 noncareful step damps horizontal by.4+abs(Y)*.2. Separate from Gel item cleanse. ThermalSpringstone produces native upward bubble column; three Magma blocks downward, native bubble movement/air callback unchanged. AirSac Boots EntityMixin records bottomInWater during tick when isInWater AND bottom-center fluid is WATER; equipped boots getGravity returns0 under that cached condition. Does not confer fall/fire/drowning immunity or damage. Native fixed movement/admission receives no Stage multiplier.

## Weapon companions

LivingEntityMixin.getKnockback adds1 when current weapon #hammers. UnrealiumCrossbow arrow independently halves LivingEntity.hurt knockback strength and AbstractArrow.doKnockback horizontal Vec3 scale. These are separate base-hit and successful-arrow enchantment knockback contributions, not two multipliers on one impulse; arrow vertical push.1 remains. Preserve native knockback resistance and rejected-hit gating. AbstractArrow mixin marks any ES-namespace CrossbowItem firedFromWeapon as shotFromCrossbow, WiltedCrossbow arrow water inertia.99, and ThrowableProjectile mixin treats WiltedPetal/EnergySpark as not in water for tick drag. No new HP source/Stage amount, but actual weapon/owner/water provenance is a future fixture.

## Native companion control

Stranghoul hirer contract admission requires Player hiring cooldown<=0, accepted hiring-food tag, adult, not already hired and targetnull. Native24000tick hire, persisted owner/count and cooldown; hirer hurt-by/hurt-target goals use changed timestamps and TargetingConditions.DEFAULT, then native Mob.setTarget. isAlliedTo accepts ordinary team OR any Stranghoul OR with hirer: hirer alliance, hirer itself, or OwnableEntity whose ownerUUID matches. Unhired Player prey additionally health ratio<.15; tagged prey excludes #stranghoul_cannot_hunt. Existing Seeds/Spear/Bow/native melee retain actual mob source, not hirer damage attribution. Native taming Moth target reset and previously resolved wantsToAttack stay in R2h4a; no repeated research or forced target bypass.

## Native supply and fire delivery

Galactic Quiver held-ammo fallback runs only when original held-projectile lookup is empty and shooterPlayer; choose first predicate-compatible stored ammo, copy and mark QUIVER_ARROW. Native useAmmo successful result with marker and ammoUse>0 consumes matching stored components; ES tick removes marker from pickup ammo/inventory. This supplies genuine existing projectile factories, no new damage/scaling; storage mechanics excluded. SaltpeterMatchbox is actual FlintAndSteelItem; registered dispenser uses BaseFireBlock placement or lights campfire/candle or native TntBlock.explode. BaseFireBlock mixin selects Abyssal/Amaramber fire by native support predicates (Amaramber later wins if both); genuine native ignition route to reviewed contact hazards. TearBomb TNT replacement remains prior native package, not a duplicate explosion implementation.

## Short exclusions

Ordinary rendering/animation/sounds, crafting/acquisition, loot/progression/book UI, storage, crop/wood/weathering/worldgen and noncombat transport omitted. SoulitSpectator is timed camera/chunk-loading projectile, no hurt payload. EyeOfSeeking is navigation information; EthericEye surface teleport/resetFallDistance is ordinary self utility with no target/combat callback. GravityPickaxe item pickup, natural600tick item repair/Crescent repair, important-item invulnerability, food-item aging, respawn dimension, attachment sync and loot targeting are utility/persistence rather than new HP/status combat mechanics. StarfireBird successful player-caused hurt only changes trust. Passive Yeti/Grimstone/Ent/Ratlin/Rookfish/Lacewing exclusions remain; flight steering and Permafrost death velocity add no offensive payload. Eight registered spell callback stubs remain return-only, no imagined fire/ice attacks.

## Compat and stage

Scoped R2h1 explicit-name scan found zero direct ES/Tensura/L2 references; generic hooks/mixins remain runtime concerns. Every native source, effect admission, hurttrue dependency, owner and iframe policy is retained. Stage belongs at final admitted native numeric damage/heal boundary, never repeated on derived Numbness debt/Starfire fraction, attributes, count/radius or binary control. Runtime fixtures, resistance/nullification intersections and source-specific mitigation need later approval; no runtime, Stage, production, Phase6/7 changes.

## TNO integration decisions

- **Dusk beam native timed fire**: COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE. Stage: Once at final native Entity.baseTick on_fire1 hurt; no beam/timer multiplier.
- **Alloy Furnace native environmental explosion**: COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE. Stage: Once per final native ownerless explosion hurt after native exposure/radius.
- **Inherited Magma/TorreyaCampfire contact HP**: COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE. Stage: Once at final native hot_floor1/campfire1 hurt.
- **Native Gel bounce and bubble movement**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: no additional multiplier; Native control/eligibility/physics remains fixed; reused damage paths retain their already-reviewed final amount point.
- **AirSac Boots native gravity override**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: no additional multiplier; Native control/eligibility/physics remains fixed; reused damage paths retain their already-reviewed final amount point.
- **Native weapon knockback and projectile-water companions**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: no additional multiplier; Native control/eligibility/physics remains fixed; reused damage paths retain their already-reviewed final amount point.
- **Stranghoul native hirer and prey targeting**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: no additional multiplier; Native control/eligibility/physics remains fixed; reused damage paths retain their already-reviewed final amount point.
- **Native Quiver and ignition source prerequisites**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: no additional multiplier; Native control/eligibility/physics remains fixed; reused damage paths retain their already-reviewed final amount point.

[Machine-readable packages, delivery paths and future fixtures](eternalstarlight-r2h8a-closure.json). Exact archive/method witnesses and targeted semantic assertions are reproducible. No whole-mod completion claim.

Exact next task: R2h8b: deterministic ES package/path deduplication, whole-source disposition map, promotion to all five views/ledger, full validation and five tooling tests, push/live verify. Then Bosses Rise native combat foundation automatically while healthy.
