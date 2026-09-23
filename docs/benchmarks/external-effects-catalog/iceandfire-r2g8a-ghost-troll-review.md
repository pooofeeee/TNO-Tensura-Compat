# R2g8a — Ghost, Troll and Myrmex disposition

Ghost/Troll, related sword/armor callbacks complete; Myrmex absent in installed JAR. Other Ice & Fire combat pending.

Static subsection complete. Runtime fixtures unexecuted; no Stage or production implementation.

## Ghost body

GhostAICharge with actual target/not charging starts approach then rush; no-animation+distance<1.4 starts Hit. Ghost.aiStep Hit ticks4 and5 with current target/distance<1.4 calls inherited Mob.doHurtTarget, no new LOS. Exact Mob reads ATTACK_DAMAGE, vanilla mob_attack direct=causing=Ghost, server EnchantmentHelper.modifyDamage, then hurt. Only hurt true enables native knockback/postAttack effects/setLastHurtMob. Natural Player/Villager acquisition does not require sight. noPhysics=true each aiStep and noGravity=true permit native phasing; not magical damage identity. Chest startOpen outside PEACEFUL creates persistent Ghost once per saved generatedGhost unless configalwaysSpawn, sets noncreative opener target and fromChest=true; distinct summon path retains same body source.

## Ghost defense

Reject Poison/Wither effects before parent canBeAffected; isInvulnerableTo adds IS_FIRE and exact IN_WALL/CACTUS/DROWN/FALLING_BLOCK/FALLING_ANVIL/SWEET_BERRY_BUSH to parent. Does not generally reject magic/arrow/wither DamageSource solely because effect immunity. Unpushable and not petrifiable. Server day gate uses level.isDay, BLOCK light>0.5 and canSeeSky at y+4 (Boat y+1), !fromChest. Day mode zeros motion, isNoAi/isSilent true, after100ticks invisible; leaving resets counter/invisibility to native Invisibility effect. This is activity/invisibility control, not daytime hurt immunity. Existing Hit animation checks are outside day branch. Saved mode/counter/fromChest persist; visual scare/haunted manuscript cosmetic excluded.

## Ghost sword launch

Native Iaf LivingEntityMixin injects swing(hand,boolean) HEAD, checks swung-hand SUMMON_GHOST_SWORD tag and config phantasmalBladeAbility(snapshottrue). Ability only Player, but reads MAINHAND stack regardless of triggering hand, tests its item cooldown, sums raw ATTACK_DAMAGE modifier amounts without attribute-operation/slot evaluation, baseDamage=.5*sum. Creates owned GhostSword with firing stack, shoots speed1/inaccuracy.5, adds entity, consumes durability1 mainhand, cooldown10. No whole-method server guard or attack-strength gate. Mainhand/offhand asymmetry and client/server spawn/event counts require native runtime fixture. Ordinary GhostSwordItem melee remains standard SwordItem, separately scaled once.

## Ghost sword impact

GhostSword extends AbstractArrow; custom tick first calls super.tick, then sets noPhysics=true and performs an additional entity sweep from current position to position+velocity. Block collider clip truncates that sweep but block result is not onHit; phasing occurs through movement, not guaranteed immediate through-wall hit. Custom sweep performs Player-owner PVP eligibility then direct onHit, no onProjectileImpact or hitTargetOrDeflectSelf; superclass first-tick route can still use those hooks before noPhysics set. Parent normal admission/findHitEntity remains. onHitEntity requests ceil(max(speed*baseDamage,0)) plus native crit RNG. Living owner => indirect_magic direct=GhostSword,causing=owner; absent/nonliving owner => ownerless magic. Neither identity becomes arrow/projectile merely from its entity class. Ordinary hurt/Tensura/L2 rules remain.

## Ghost sword returns

On-fire projectile ignites non-Enderman5seconds before hurt, with no restore on rejection (saved fireticks unused). Hurt true: Enderman immediate return; otherwise optional push via private knockbackStrength*.6 +Y.1, calls inherited doPostHurtEffects (empty in exact class), then discard if pierce<=0. No explicit EnchantmentHelper.doPostAttackEffects in custom hit. Hurt false reverses velocity*.1 and discards on server if speedSquared<1e-7. Native superclass constructor copies firing weapon, processes projectile-spawn enchantments and piercing count. Subclass piercedEntities differs from superclass piercingIgnoreEntityIds used by inherited canHitEntity: do not assume reliable unique-target piercing or safe loop termination for nonzero PierceLevel. Native nonzero-pierce availability must be checked before any later fixture; no fabricated enchant/packet. Standard launch does not set private punch or critical flags.

## Troll body explosion

Troll.doHurtTarget randomly selects horizontal/vertical Strike and returns true without damage. aiStep tick10,current target,rangeSquared<4,deathTime<=0 requests ATTACK_DAMAGE mob_attack direct=causing=Troll. Horizontal additionally SETS target velocity=(sin(yaw),cos(yaw),.4), independently of hurt; this is not ordinary knockback/resistance. When navigation done,target at squared distance>3 and<30,mobGriefing true, it can start vertical Strike random1/15 and at tick10 manually constructs vanilla Explosion at weapon offset, radius1+randomFloat, firefalse,BlockInteraction.KEEP; Iaf grief veto gates explode/finalize. Native default player_explosion direct=causing=Troll, inherited entity damage/knockback/detonate hooks; no Level start hook and no block destruction. Overlap3<distanceSquared<4 can request melee plus explosion same frame. Roar only sound.

## Troll regen conversion

When not statue,injured,tickCount%30==0 Troll attempts Regeneration30ticks amp1 hidden particles/icon. Exact RegenerationMobEffect heals1 if below max, interval50>>amp=25 using remaining duration; effect/HealEvent rejection preserved. Daytime server SKY light>0.5+canSeeSky at feet (Boat above) creates StoneStatue snapshot and removes Troll KILLED regardless of addFreshEntity success, without hurt/GORGON source or death protection. Protected statue persistence applies. This conversion is binary, not huge numeric HP damage. Native hurt rejects any source msgId containing lowercase arrow; it is not IS_PROJECTILE immunity. Armor9 and knockbackResistance1 native baselines; neither prevents custom direct velocity changes.

## Armor real hook

ServerEvents.onEntityDamage computes TrollArmor IS_PROJECTILE reduction factors per HEAD.1/CHEST.3/LEGS.2/FEET.1 (full factor.3). Same callback handles exact DRAGON_FIRE/ICE/LIGHTNING holders for DragonScale/Steel armor with same weights; overlapping conditions sequentially multiply. BUT installed Uranus dispatch is PlayerEntityMixin ModifyExpressionValue at Math.max(FF) in Player.actuallyHurt, not a generic damage event for every LivingEntity. Exact NeoForge21.1.244 has ONE such call: setAbsorptionAmount(max(0,absorption-absorbed)), after armor/magic/onLivingDamagePre. Therefore absent another mod transformation, callback multiplies remaining absorption, NOT final HP damage; DamageContainer.newDamage used for HP is unchanged by this hook. It may consume extra leftover absorption and has no direct value when zero. Uranus DAMAGE returns on first callback that changes amount. This pinned static mismatch must be tested with real installed mixin composition; do not claim intended projectile/dragon HP reduction or apply Stage at this expression.

## Troll weapon

Troll weapons have ordinary sword damage/speed attributes and no extra hurt request. Player hurtEnemy returns cooldown<.95 OR attackAnim!=0; this occurs in native post-hit item handling and does not itself veto already applied HP damage. Nonplayer delegates parent. inventoryTick selected+cooldown<.95+attackAnim>0 decrements swingTime. Declared onEntitySwing(LivingEntity,ItemStack) has reversed arguments versus exact NeoForge IItemExtension(ItemStack,LivingEntity[,hand]); TrollWeapon does not implement Uranus ISwingable either. No native caller proves that custom swing method runs. Treat it as inactive signature, not a verified attack block. Standard melee covers damage once; animation/cost detail no Stage value.

## Myrmex

Installed archive census finds zero Myrmex-named entries and zero Myrmex class constants. No native entity/item/status registry or combat implementation to catalog for this installed build. Excluded as absent, not inferred from older Ice & Fire versions.

## Compatibility

No direct SHP writes. GhostSword indirect_magic versus Ghost/Troll mob_attack and real explosion tags are materially different Resistance/Nullification/L2 inputs; preserve them. Numeric damage or native heal amounts get one downstream amount point. No Stage on phasing, daytime activity, statue conversion, vanilla regeneration duration/amplifier, native immunity, armor percent or remaining absorption. No production fix for Uranus hook, GhostSword callback or Troll swing signature is authorized.

## Exclusions

Rendering, jump scare, colors/manuscript, lore, drops, crafting, armor models and world generation excluded. Chest summon retained because it changes combat target/day admission. Myrmex absent. All future runtime fixtures remain unexecuted.

## TNO integration decisions

- **Ghost/Troll melee and native swords**: NUMERIC_SCALABLE, VANILLA_ROUTED, ADMISSION_GATED. Stage: yes; Once at native target.hurt request after native attack attribute/enchantment calculation; Ghost inherited Mob, Troll aiStep, sword ordinary Player attack.
- **Ghost Sword magic projectile damage**: NUMERIC_SCALABLE, VANILLA_ROUTED, ADMISSION_GATED. Stage: yes; Once at GhostSword.onHitEntity hurt amount after native speed/ceil/crit formula, not at both summed weapon modifier/baseDamage and impact.
- **Ghost Sword native impact control/fire/lifecycle**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: no additional value; Ignition native timer; generic on_fire damage only once downstream. Preserve hurt-success push and failure bounce; no synthetic projectile hook.
- **Ghost phasing, effect immunity and daytime inactivity**: BINARY, ADMISSION_GATED, NO_STAGE_VALUE. Stage: no additional value; Activity and native source/effect gates are not damage amounts.
- **Troll weapon explosion HP damage**: NUMERIC_SCALABLE, VANILLA_ROUTED, ADMISSION_GATED. Stage: yes; Once at inherited Explosion final target.hurt amount, not radius/visibility/source.
- **Troll strike motion, arrow veto and sunlight statue conversion**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: no additional value; Native fixed velocity, msgId veto and binary replacement remain native.
- **Troll vanilla regeneration**: NUMERIC_SCALABLE, VANILLA_ROUTED, ADMISSION_GATED. Stage: yes; Once at native RegenerationMobEffect heal(1) through LivingHealEvent; no multiplier on status duration/amplifier.
- **Troll/Dragon armor installed absorption hook**: CUSTOM_ROUTED, ADMISSION_GATED, NO_STAGE_VALUE. Stage: no additional value; Never scale this remaining-absorption expression. Intended HP mitigation is not proven in installed loader; test native composition first.

[Machine-readable packages, native paths and future fixtures](iceandfire-r2g8a-ghost-troll.json). Validation reproduces new witnesses, checks significant call order/amounts, preserves accepted records and prior evidence, runs five tooling tests and diff checks. No whole-mod completion claim.

Exact next task: R2g8b: Hydra/Sea Serpent/Stymphalian/Amphithere and combat-special Hippogryph/Hippocampus; remaining special equipment/status/custom DamageTypes and whole-mod closure/dedup/promotion. Static only.
