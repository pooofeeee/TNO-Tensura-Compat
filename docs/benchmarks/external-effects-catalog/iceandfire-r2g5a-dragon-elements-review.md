# R2g5a — Dragon elemental combat paths

Frozen/Siren/Gorgon protected; Fire/Lightning elemental paths, optional explosion and terrain hazards reviewed. Shared dragon melee/defense/healing and other families still pending.

Static subsection complete. Runtime fixtures unexecuted; no Stage or production implementation.

## Scope

Fire/Lightning elemental delivery deltas and shared optional charge explosion/terrain hazards are complete. Frozen is reused, not re-researched. Shared dragon melee, roar, defense, age attributes and healing remain R2g5b. Native dragon age tier1..5 is not TNO Stage.

## Native entries

Fire/Lightning.aiStep server target/ground FIRE dispatch -> shootFireAtMob. Ground random1/5 or airborne HOVER_BLAST branch starts FIRECHARGE and creates subtype projectile at animation tick20; otherwise starts breathing and requires isActuallyBreathingFire before breathAttack(false). Their riderShootFire random1/5&&!baby also launches tick20, otherwise native controller ray10*tier -> breathAttack(false). This differs from protected Ice AI/rider tick15. Shared flight HOVER calls breathAttack(true)->performChargeAttack tick20; SCORCH_STREAM waits for actual breath and targets moving ground point. Shared legitimate forge burningTarget can cause collateral Fire/Lightning breath. Owner/control packet, age/sleep/dead and breathing warmup remain R2g2b prerequisites; do not directly invoke manager in runtime fixtures.

## Sampling

Fire uses inherited DragonBase.performNormalBreathAttack, including navigation.stop. Lightning overrides that method: same burnProgress/40, sample spacing ceil(conqueredDistance/100), obstruction ray and visible jittered endpoint area dispatch; visible samples update lightning target data rather than spawning damage entities. Lightning override does not call navigation.stop. No actual vanilla LightningBolt is spawned by this breath. Shared breathAttack event ON_DRAGON_FIRE_BLOCK may veto; manager ON_DRAGON_DAMAGE_BLOCK may veto entire area. Multiple sampled areas can produce multiple hurt requests; no one-hit-per-cast guarantee.

## Breath amounts

Manager Fire requested HP=tier*attackDamageFire(snapshot2.0), then igniteForSeconds(5+5*tier). Lightning requested HP=tier*attackDamageLightning(snapshot3.5), then knockback(0.3,dragonX-targetX,dragonZ-targetZ). Ice Frozen values remain protected. Area query default nonspectator, !DragonUtils.onSameTeam,!self,dragon LOS; radius/tier sampling exactly R2g2b. Terrain grief gates do not gate this living breath loop. Hurt boolean discarded before secondary effect; knockback/ignition do not imply any damage was admitted.

## Charge amounts

Shared DragonCharge owner/current-rider routing, collision early returns and native TamableAnimal self-owner predicate remain R2g2b. Fire direct request=tier*attackDamageFire; Lightning=tier*attackDamageLightning. Direct source uses current rider else Dragon as BOTH direct and causing; source is not projectile and direct hit does not itself ignite/knockback/Frozen. Surviving non-MISS collision with Dragon canGrief reaches charge area: max(1,tier-1)*2 requested HP, then Fire15seconds or Lightning knockback0.9. Area filters !isAlliedTo,!self,LOS; radius and mobGriefing distinctions reused. Direct hurt result discarded; discard does not skip following area.

## Charge subtypes

FireCharge overrides isPickable=true while inherited hurt always false and shared tick bypasses AbstractHurtingProjectile impact/deflection route. Its tick discards in water but continues to super.tick without return; do not promise no same-tick collision after water removal. It also ignites itself when shouldBurn. LightningCharge implements IDragonProjectile; FireCharge does not. Shared onHit early return for an IDragonProjectile collision therefore distinguishes subtype targets. No native successful attack-reflection ownership change is implemented by these classes; projectile owner stays Dragon.

## Source identity

Protected exact factories: manager unmounted Fire=dragon_fire and Lightning=dragon_lightning, direct=causing=Dragon. With current Player controller manager direct=Dragon,causing=Player; indirect Lightning factory actually selects dragon_ice. Direct Lightning charge selects dragon_lightning even ridden. Optional manager explosion inherits the manager source, so ridden Lightning explosion also carries ICE. Existing compat classifies actual holder fire/cold/lightning and not physical. Scoped tags do not grant these custom types IS_FIRE,IS_LIGHTNING,IS_PROJECTILE or IS_EXPLOSION merely because of appearance/delivery; only always_hurts_ender_dragons was found. Secondary on_fire/in_fire/cactus use their own native identities and ownerless attribution.

## Fire lifecycle

igniteForSeconds floors seconds*20; igniteForTicks only raises remainingFireTicks. Damage denial does not veto timer write. Exact Entity.baseTick server positive fire: fireImmune reduces timer by4 without pulse; otherwise every timer%20==0&&!isInLava requests on_fire1 then decrements1. Fire resistance and native damage hooks still decide HP. Client baseTick clears timer. Ice/Frozen/fire removal interaction stays the accepted R2g2a contract. No custom owner-bearing delayed Fire source is created.

## Knockback

Lightning secondary calls native LivingEntity.knockback independently of hurt success. Exact method first exposes LivingKnockBackEvent (cancel/strength/vector), multiplies strength by1-KNOCKBACK_RESISTANCE, halves horizontal existing velocity and subtracts normalized direction; grounded Y=min(.4,oldY/2+strength). This is separate numeric control, not added HP. Leave native control strength/admission unchanged for TNO damage scaling.

## Optional explosion

After charge area/status, explosiveBreath(snapshotfalse) creates BlockLaunchExplosion(world,dragon,SAME manager source,center,min(2,tier-2),mode). mobGriefing chooses DESTROY or KEEP; KEEP still explodes/damages. Native radii by age tier are -1,0,1,2,2, with no clamp in constructor; early-tier edge behavior needs runtime tests, no repaired radius. It calls explode/finalizeExplosion directly, not Level.explode and its start hook. Inherited exact Explosion.explode still calls onExplosionDetonate, filters ignoreExplosion/distance/calculator, requests calculator damage with supplied source, then independent explosion knockback/event. No dragon-team exclusion is added to this explosion; initial source Dragon is excluded from query. R2g1 source identity and native hurt restrictions remain.

## Explosion amount

Inherited calculator for normal positive radius uses f=2*radius, normalized distance d and sampled visibility v; impact=(1-d)*v, requested amount=(impact^2+impact)/2*7*f+1. It is an additional request beyond direct hit and manager area. Knockback uses explosion resistance and getExplosionKnockback event independently of hurt result. EntityBased calculator inherits entity damage methods and customizes block resistance/destruction only (protected raw fallback witness). Do not multiply radius/visibility/knockback as a shortcut to scaling numeric damage.

## Explosion finalize

Custom finalize replaces selected nonair blocks with AIR and calls wasExploded when mode!=KEEP; it constructs FallingBlockEntity and assigns position/velocity but NEVER adds it to the level or enables falling hurt. Therefore no native spawned falling-block combat delivery is proven. Block destruction itself can affect cover, not a fabricated damage family. Source/witness kept; no utility rendering archaeology.

## Terrain hazards

attackBlock respects DragonProof/canDragonBreak and transforms block. Fire may place vanilla FIRE above with random1/2; Ice may place dragon_ice_spikes with random1/9, under solid transformed ground, original occlusion, above fluid empty/nonoccluding/breakable. Lightning places no analogous hazard. Native fire contact BaseFireBlock increments timer for nonfireimmune (zero-crossing ignite8seconds), then requests in_fire/fireDamage regardless of that immunity branch; ordinary fire resistance/parent hurt decide. IceSpikes.stepOn excludes IceDragon, requests cactus1, then if Living and BOTH motionX!=0 AND motionZ!=0 requests knockback.5 even hurt=false. Existing compat cancellable HEAD vetoes whole step for toggled ColdResistance/Nullification or ThermalFluctuationResistance/Nullification (same toggled/mastery helper); no Frozen or cold DamageSource is added. Spike support loss removes block. Placement and destruction do not justify duplicate Stage multipliers.

## Runtime limits

Installed configuration snapshot is evidence, not proof of loaded runtime values. Runtime tests must verify source holder/direct/causing, native event vetoes, HP/SHP and separately ignition/Frozen/velocity. Compat declarations are not runtime mixin certification. No L2 testing, new damage source, fallback, production or Stage change.

## Excluded

Breath particles, lightning renderer/target vectors and sounds are appearance only; recipe/forge acquisition internals, block palette/cosmetic transformations and unspawned falling-block appearance receive short exclusions. Combat cover changes and actual fire/spikes stay represented.

## TNO integration decisions

- **Dragon elemental HP requests**: NUMERIC_SCALABLE, CUSTOM_ROUTED, ADMISSION_GATED. Stage: yes; Each native target.hurt amount once: manager breath/charge loop or DragonCharge.onHit direct request. Use a single downstream Stage amount layer for each event, never also multiply native age/config or projectile and area together.
- **Dragon Fire ignition and pulses**: COMPOSITE, VANILLA_ROUTED, NUMERIC_SCALABLE. Stage: yes; The existing on_fire damage pulse amount at Entity.baseTick -> hurt, once; do not multiply ignition seconds, timer and pulse together or synthesize Dragon attribution.
- **Dragon Lightning area control**: CUSTOM_ROUTED, ADMISSION_GATED, NO_STAGE_VALUE. Stage: no additional value; Native .3/.9 knockback is control and retains event/resistance rules; no additional TNO damage multiplier.
- **Optional dragon charge explosion**: NUMERIC_SCALABLE, COMPOSITE, ADMISSION_GATED. Stage: yes; Inherited Explosion.explode -> entity.hurt(calculator amount) once; preserve explicit manager source. Never scale explosion radius and damage amount together.
- **Dragon-placed vanilla fire contact**: VANILLA_ROUTED, NUMERIC_SCALABLE. Stage: yes; Existing BaseFireBlock.entityInside -> hurt(in_fire,fireDamage) once; delayed on_fire pulse belongs to ignition package, not another copy.
- **Dragon Ice Spikes contact**: COMPOSITE, VANILLA_ROUTED, ADMISSION_GATED, NUMERIC_SCALABLE. Stage: yes; IceSpikes.stepOn -> hurt(cactus,1) amount once after native/compat admission. Leave .5 knockback and placement frequency unchanged.

[Machine-readable packages, native paths and future fixtures](iceandfire-r2g5a-dragon-elements.json). Validation reproduces new witnesses, checks significant call order/amounts, preserves accepted records and prior evidence, runs five tooling tests and diff checks. No whole-mod completion claim.

Exact next task: R2g5b: Dragon shared melee/rider tackle and shake-prey attacks, roar effects, native age attributes, defenses/model-death and healing/resource hooks; then Cockatrice. Reuse R2g1 source foundation, R2g2b Frozen/common delivery and R2g5a elemental paths. No runtime/L2/Stage/production.
