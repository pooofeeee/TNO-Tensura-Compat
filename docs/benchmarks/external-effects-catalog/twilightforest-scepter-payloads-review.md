# r2f8j - TWILIGHT_SCEPTER_PAYLOADS_SEMANTIC_REVIEW_COMPLETE

Installed TF4.8.3345, raw Minecraft1.21.1 and exact NeoForge21.1.244. Static source review only. Damage request, final HP, execution/removal, motion, shield count and durability are separate. Protected Lich boss shield, Twilight bolt and R2f8i recharge contracts are reused unchanged. No runtime/L2/Stage/production or balancing fix.

Adds 7 reviewed packages / 26 delivery cases. Twilight remains PARTIAL at 132/400 drafts, zero promoted. REVIEW_REQUIRED 0.

## Native contracts

### Authority

Installed TF4.8.3345, raw Minecraft1.21.1 and exact NeoForge21.1.244. Static source review only. Damage request, final HP, execution/removal, motion, shield count and durability are separate. Protected Lich boss shield, Twilight bolt and R2f8i recharge contracts are reused unchanged. No runtime/L2/Stage/production or balancing fix.

### Fortification use

Native Fortification Scepter use fails damage==max && !instabuild. On server sets temporary shields to5 (not adds; permanent count preserved), then noncreative-material cost1 through protected nonbreaking helper. Capacity9. Sound and SUCCESS; if !Player.isCreative adds native item cooldown1200. isCreative and instabuild are distinct predicates. Ordinary ServerPlayerGameMode.useItem rejects spectator/cooldown before ItemStack.use. No Crown use-cost discount, direction check or HP operation.

### Shield counts

Attachment defaults temporary0/permanent0/timer240. setShields clamps selected count0..115; temporary set always resets timer. addShields clamps integer addition0..115; temporary timer resets only if old temporary<=0. Addition is int before cast to long, so extreme administrative amount can overflow. Other count preserved. Ordinary mutators allow115 each/230 total; two-int codec constructor only clamps negative to0, no upper115 clamp. Sum uses int. breakShield prefers temporary, decrement+timer240; otherwise permanent decremented. No HP write. Non-expired ServerPlayer break awards statistic. Sound/setData occur even zero if method directly called, but native event/timer callers guard positive counts.

### Shield producers

All installed-TF instruction census: FortificationWand.use sets5 temporary; ShieldCommand set/add are the other actual producers. Permission2 native /twilightforest shield <single entity> set|add <int amount> [temp boolean], aliases tf/tffeature, default temp=true. Only LivingEntity receives mutation; command returns1 even other target. Permanent shields therefore have a legitimate administrative path, not a proven survival producer. Attachment event and timer break existing resources. Lich boss shield count is unrelated.

### Shield admission

CapabilityEvents setup installs ordinary LivingIncomingDamageEvent listener. On server and source NOT BYPASSES_ARMOR, obtains attachment; if total>0, if invulnerableTime<=0 breaks one (temporary first), particles, sets invulnerableTime20; then always cancels incoming event, including the last-shield hit and positive invulnerableTime hits that spend no shield. No amount threshold, facing, held shield, armor, attacker, direct entity, source position or player predicate. BYPASSES_SHIELD alone does not bypass this attachment; BYPASSES_ARMOR does. Particle source/owner lookups affect visuals only. Native incoming event precedes ordinary shield blocking, cooldown and final mitigation, so charge consumption does not require an otherwise-successful HP hit. Earlier native immunity/client/dead/fire-resistance rejection and Player admission/difficulty still precede it. Listener registration does not establish order against every other mod; existing cancellation/event behavior remains native. Cancellation yields false hurt and no final HP damage in this native path.

### Shield timer

EntityTick.Post: server Living with existing attachment -> tick. Temporary>0 and nonPlayer OR !Player.abilities.invulnerable. At timer<=0 breaks one expired shield/reset240; else decrements unless HEAD MysticCrown AND tickCount%3==0. Normal fresh240 lasts240 decrements plus next eligible callback to break; Crown skips one in three decrements, phase-dependent duration, not a universal fixed wall-clock interval. Damage break also resets timer. Permanent never expires. Invulnerable Player pauses temporary ticking; world unload has no offline countdown.

### Shield persistence

Registered serialized/synced codec stores only temporary_shields/permanent_shields, not timer. Exact244 Entity save/load uses neoforge:attachments; constructor resets timer240 on decode. AttachmentType default copy serializes/decodes, so eligible copies also reset timer. No copyOnDeath configured: Player death Clone excludes it even keepInventory; non-death Clone copies it. Native living conversion uses copyEntityAttachments(...,true), therefore excludes this attachment. This is count persistence, not preserved remaining duration. Native sync transports both counts; no owner/master shared-resource link.

### Drain use

Lifedrain capacity99/shared resource protected. use fails fully damaged&&!instabuild, else starts native hand use. onUseTick stops on damage==max even creative. Use duration72000, BOW animation; native updateUsingItem runs EventHooks.onItemUseTick then positive-remaining callback, then decrements count. Attempt when remaining count%5==0. canContinueUsing same item ignores component changes; actual hand stack continuity/native use events remain. No bespoke cooldown, physical hit, projectile spawn, ammo, enchantment requirement or damage-helper call. Native recipient cooldown remains, so every5 attempt is not every5 HP loss.

### Drain selection

getPlayerLookTarget uses eye/view segment20 and casterBB expanded view*20 inflated1, native level.getEntities excluding caster. Candidates only isPickable, inflated getPickRadius AABB segment clip. No block ray/LOS, distance attribute, friendship or boss prefilter. Chooses nearest positive intercept with hitDist=0 sentinel; origin-inside candidate sets0, which a later candidate can replace (list order/inside-zero quirk). Final selected entity must Living and not ArmorStand; a selected nonliving/ArmorStand prevents this attempt, no rescan. Living native isPickable excludes removed; dead checks for particles do not add a global pre-hurt alive gate. No claim of universally nearest selection when origin is inside boxes.

### Drain source

Only actual LIFEDRAIN instruction caller is LifedrainScepterItem.onUseTick. Initial native target.hurt(request1) with direct=causing=caster LivingEntity, position from direct entity. Type exhaustion0/scaling when_caused_by_living_non_player. Tags exactly bypasses_armor, bypasses_shield, bypasses_wolf_armor, is_projectile, neoforge:is_magic. It is tagged projectile without a projectile entity. Native Resistance/protection (including applicable projectile protection), absorption, invulnerability, cooldown, PvP/source/event admission remain; no bypass resistance/enchantments/cooldown/invulnerability. Player caster avoids nonPlayer difficulty scaling. Fortification skipped by armor bypass. No fabricated source or guaranteed1 HP loss.

### Drain branch

Outer secondary branch requires initial hurt true and server; true does not guarantee positive HP loss (absorption/events). Tests target CURRENT HP<=1 && !c:bosses AFTER initial request. Low nonboss takes execution branch; otherwise native Slowness20/amp2 (SlownessIII, -.45 base movement attribute) and if remaining count%10==0 caster.heal1, then Player FoodData.eat(1,.1). Food native add clamps food0..20, saturation0..food, giving up to1 food/.2 saturation. Heal and food independent of effect admission/heal return and hunger/fullHP need. No effect causer passed. c:bosses prevents execution only, not damage/slow/restore/motion. Low nonboss branch does not give slow/heal/food. Cadence plus native recipient cooldown can suppress later healing; no constant regeneration claim.

### Drain execution

Within true initial hurt/server/lowHP/nonboss: if target lacks LIFEDRAIN_DROPS_NO_FLESH and caster Player, evaluates native bonus loot at target eye with target/source and caster Player attribution, spawns items and shatter particles. Native data bonus is uniform0..2 rotten flesh; no extra damage/explosion from visual big shatter. Target Mob spawnAnim; optional reflected native death sound. Then only if target !isDeadOrDying: Player gets a second same-type request Float.MAX_VALUE, ignored return, ordinary admission/totem can prevent death. NonPlayer instead native die(source) followed unconditionally by discard(); no second hurt/HP subtraction. die runs native Death hook, but ignored/canceled death does not prevent following discard. This removal can occur while HP remains positive and bypasses a second mitigation/totem check; it is existing native code, not an authorized compatibility implementation. If first request already killed, bonus/sound still run but extra die/discard skipped. NO_FLESH suppresses only bonus/shatter, not execution. Native bonus loot is independent of ordinary death loot rules/hook result; this method does not check doMobLoot before bonus.

### Drain motion

After and independent of initial hurt-success branch: server && target.currentHP<=caster.currentHP -> target.setDeltaMovement(0,.15,0). Replaces XYZ, not additive push, with no knockback-resistance/effect-immunity/LOS/team/hurt-return gate. Comparison follows possible caster healing/execution. Failed/immune hurt can still satisfy motion condition. Calls on already removed/dead object do not prove subsequent world movement. No Levitation effect, launch attachment, source rewrite or fall immunity.

### Drain resource

Only initial hurt true/server reaches Player non-instabuild durability request1, after whichever secondary branch. HEAD MysticCrown skips request when randomFloat<=.05; no Crown means always request1. Shared Unbreaking/Unbreakable/item hooks may change applied cost; native resource helper is protected R2f8i. No cost from false hurt, no healing required, no double cost for second execution request. Direct scepter damage is unaffected by Crown chance.

### Living source hooks

Because direct entity is caster Living, protected TF ToolEvents use its current MAINHAND independently of used hand or projectile tag. Legitimate offhand Lifedrain while mainhand Knightmetal sword/pick qualifies for protected armored-target bonus; mainhand Knightmetal axe with target armor0 sets original incoming damage+2. Normal mainhand scepter does not qualify. MinotaurAxe bonus also requires current isSprinting; retain that conditional without asserting sustained native sprint while using. Native use/recipient gates and event ordering remain. This source identity does not pass through Mob/Player melee enchantment helpers; no invented Sharpness/Strength addition.

### Twilight crown

Twilight Scepter use: exhausted&&!instabuild FAIL, otherwise server addFreshEntity(new TwilightWandBolt(level,player)), add return ignored before possible charge. Non-instabuild request1 unless HEAD Crown and randomFloat<=.05. No item cooldown. Capacity99 and recharge protected R2f8i; bolt damage/reflection/source paths protected R2f3, not duplicated. Crown never worn down here. Zombie Crown baby producer remains protected; Fortification Crown affects timer rather than use cost. Crown armor material/other gear effects remain separate.

## Packages

| Mechanic | Primary classification |
|---|---|
| Temporary and permanent Fortification shields | CUSTOM_RESOURCE |
| Fortification incoming damage cancellation | BINARY_MECHANIC |
| Lifedrain native selection and custom damage | CUSTOM_DAMAGE |
| Lifedrain low-health execution and bonus loot | BINARY_MECHANIC |
| Lifedrain admitted slow and caster restoration | VANILLA_COMPOSITE |
| Lifedrain independent vertical motion replacement | CUSTOM_CONTROL |
| Crown scepter charge-saving branch | CUSTOM_RESOURCE |

## Custom source callers

| Type | Amount | Source identity |
|---|---|---|
| twilightforest:lifedrain | Initial1 each eligible remaining-count%5 attempt; true/low nonboss/alive Player branch requests Float.MAX_VALUE separately. NonPlayer die/discard is not a second HP request. | Both caster LivingEntity; no projectile entity, despite IS_PROJECTILE tag. |

## Scope and exclusions

- Five complete native class surfaces and selected native event/registration/source consumers; all-TF relevant caller scan.
- Lich boss shields remain distinct; Twilight bolt, Zombie Crown baby and shared recharge protected, not duplicated.
- Crown armor/other items/charms/hazards/nested ASM and whole-mod compatibility closure still pending.
- Native die/discard and independent motion documented as installed; no repair/compatibility implementation.
- LIFEDRAIN USED:28/40 custom types reviewed,12 unfinished. Twilight PARTIAL, zero promoted, REVIEW_REQUIRED0.

## Future native controls

- Native Fortification use/cooldown/admin counts, last-shield/repeated-hit/bypass and timer/save/clone controls.
- Real Lifedrain ray/pickability/occlusion/use scheduling with intact source/defense/cooldown.
- Distinct low-HP Player hurt versus nonPlayer die/discard, boss/no-flesh/bonus-loot and initial-death controls.
- Separate admitted slow/heal/food, independent health-gated motion and real offhand source-identity hooks.
- Crown cost requests with protected charge/recharge/projectile controls.

[Semantic packages and paths](semantic-sections/twilightforest-scepter-payloads.json), [integrity](twilightforest-scepter-payloads-integrity.json), [full validation](r2f8j-scepter-payloads-validation.json).

Exact next task: Continue Task C with remaining player projectile/utility weapons (Moonworm Queen, Cube of Annihilation, Ender/Seeker/Triple bows, Peacock Fan), then armor/charms/food, remaining utility/passive entities and hazards/custom sources, exact nested ASM/compatibility coverage. Twelve custom types remain unfinished. Protect every subsection toward R2f8, then deduplicate/promote whole Twilight. IceAndFire only after Twilight COMPLETE is pushed/live verified. No runtime boss/L2/Stage/production/fixes/Phase6/7.
