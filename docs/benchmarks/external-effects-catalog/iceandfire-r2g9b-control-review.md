# R2g9b — Control, Pixie and combat support

Chain/flute/Pixie/food and remaining lightning armor/death-summon hooks reviewed; final closure and promotion pending.

Static subsection complete. Runtime fixtures unexecuted; no Stage or production implementation.

## Chain delivery

ChainItem.interactLivingEntity rejects clicked target CHAIN_UNTIEABLE (installed Player/EnderDragon/Wither) or already chained to interacting Player. Ordinary chain attaches Player UUID; sticky chain, within Player-centered+-60 cube, redirects every nearby Living already chained to Player onto clicked target UUID, without per-nearby immunity/ownership/LOS checks; if none, attaches clicked target to Player. Sticky sneaking instead clears clicked target links and removes its UUID from nearby entities, then returns before cost. Already-chained early return precedes this clear branch. Noncreative normal attach/retarget costs1 item. Native mechanics are movement control, not HP damage or native leash range; no Stage scaling.

## Chain compat

Installed MixinItemChain injects BEFORE ChainData.attachChain invocations inside interactLivingEntity and cancels with PASS if CLICKED target has tensura_iaf:cannot_be_chained. Tag contains #tensura:boss_for_hero plus listed Tensura/optional NEB bosses. It does not test each retargeted nearby entity or hook general ChainData.tick/attachToFence/tie transfer. Sticky retarget has removed old UUID links before attach injection can cancel; cancellation does not undo earlier removals. Preserve this exact hook/partial side effect and runtime mixin admission. No generic Tensura/L2 control immunity can be inferred.

## Chain tick

IafAttachments @SubscribeEvent EntityTickEvent.Post ticks/syncs ChainData for LivingEntity. Attachment serializes UUID list, syncs and copyOnDeath; no duplicate UUID attach. Server tick resolves each anchor only in same ServerLevel; if distance>7 adds (x*abs(x)*.4,y*abs(y)*.2,z*abs(z)*.4), where xyz is unit direction toward anchor. Multiple anchors add independently. No Living.knockback, knockback-resistance check, effect admission, LOS, hard freeze or HP request. Missing/unloaded/different-dimension anchor simply gives no force; UUID is not automatically removed, so force can resume when resolved.

## Chain release

WallBlock useOn calls attachToFence server; RIGHT_CLICK_BLOCK event also does so, without requiring ChainItem in hand. It transfers links from Player to a ChainTie within+-30 cube. Tie.interact transfers current Player links, else removes tie, with no ownership gate. Tie hurt requires causing entity Player then inherited BlockAttachedEntity hurt: native invulnerability can reject, otherwise server kills tie even amount0; this is binary destruction, not numeric HP. Tie survives only WallBlock and inherited support tick can discard it. On any remove reason, tie clears its UUID on nearby Living within+-30 and returns chain items; farther/unloaded links remain unresolved. Death event clears the dying entity own links before returning PASS, independent of later death cancellation. ServerEvents.onEntityInteract checks target chained to ITS OWN UUID, not interacting Player UUID; it does not generally detach a normal Player anchor. Native sticky clear/tie removal remain legitimate release paths.

## Flute

DragonFlute.use cooldown60, box from Player position to position+1 expanded horizontal16*configFluteDistance (snapshot8=>128) and vertical256, all IDragonFlute recipients, no LOS; sort does not limit recipient count. DragonBase.onHearFlute requires tame AND owned by Player, clears flying/hovering if set and stops navigation; Player passenger removal also calls it. Amphithere.onHearFlute only requires tame and not onGround, then sets fallen regardless of flute Player ownership. Accepted R2g8c fallen motion applies. No damage request or Stage numeric value; test owned Dragon versus other-owner tame Amphithere, not an invented generic stun.

## Pixie wand

PixieWand.use finds exact PIXIE_DUST offhand/mainhand/inventory, or allows creative/INFINITY; starts use/swing then immediate server owned PixieCharge at PlayerY+1 along noisy look. It consumes1 ammo unless creative or Infinity with dust; durability hurtAndBreak is mistakenly called on ammo variable, not wand, so do not assume advertised wand wear. Cooldown5 only when admitted. Projectile inherits normal AbstractHurtingProjectile.tick: loaded chunk and owner null/notRemoved, native ProjectileImpact cancellation/deflection and canHitEntity/noPhysics filtering. NoGravity, clearFire, shouldBurn=false, inertia1.05 outside liquid, native liquid inertia; tickCount>30 discard before super without immediate return.

## Pixie charge

Custom onHit handles only server ENTITY hits excluding owner; no super.onHit. Living recipient receives Levitation100amp0 then Glowing100amp0 BEFORE hurt5. Source is minecraft:indirect_magic with direct=SHOOTER, causing=null, not direct=projectile/causer=Player. Native ownerless spell gates must see that identity. No ally filter; native effect immunity and damage rejection are independent. Any admitted nonowner entity hit discards only when tickCount>4; early repeated contacts can reapply requests. Block hits invoke no removal/damage logic here and inherited movement continues, so wall collision does not provide an ordinary impact-stop guarantee. No custom charge reflection behavior claimed; native deflection hooks stay. Scale once final hurt5, no scaling durations, movement or projectile creation.

## Pixie aura

Tame Pixie with resolved owner at distanceSquared<100, every80 ticks, requests owner status100amp0 by clamped color0..4: Strength, JumpBoost, Speed, Luck, Haste. No LOS/sitting gate in aura branch; body may have entered storage and been removed earlier. Native effect admission/refresh and remaining duration after separation preserved. Damage-related attributes from Strength remain in normal attack formula; no extra Stage on potion amplifier/duration. Luck/Haste are recorded briefly as non-HP support, not deep research.

## Pixie theft

Native steal goal: configstealItems (saved snapshot false; availability must be checked before positive runtime fixture), wild, empty mainhand, cooldown<=0, nearest Player within10 with nonempty inventory/noncreative; random1/200 rejects rather than admits, local delay must expire. At squared distance<3 selects random nonhotbar, nonempty, stackable stack not PIXIE_STOLEN_BLACKLIST (dragon egg), moves WHOLE stack into Pixie hand via removeItemNoUpdate, then applies matching negative status100amp0: Weakness/Nausea/Slowness/Unluck/MiningFatigue. No LOS/damage/Resistance prerequisite to theft; effect admission does not undo item transfer. Sets nearby Pixie cooldown1000..3999 within inflate40, and own saved stealCooldown ticks down. Combat resource/control path, no Stage on count/duration.

## Pixie defense heal

Pixie.hurt first server random1/3 with held item drops stack, empties hand, cooldown3000, returns TRUE without parent HP damage. This can precede owner/invulnerability checks; hurt success therefore does not prove HP loss. Otherwise owner-close (<10) vetoes cached inWall or owner-caused; fallingBlock check compares freshly allocated source by identity, not effective ordinary falling-block immunity. isInvulnerableTo independently rejects owner-caused at any distance. Empty checkFallDamage suppresses natural fall callback. No broad spell immunity. Native owner hand HEAL_PIXIE+injured heal5 and consumes1 even creative; dropped goal only actual Cake whenwild or Sugar whentame/ injured, then at squared<1 tagHEAL heal5 or tagTAME+Playeritemowner tame/sit. Keep heal event and item/tame side effects independent. Scale once heal5, never HP subtraction or status-duration changes.

## Foods

Native Item food completion->LivingEntity.eat/addEatEffect server issues independent addEffect requests at declared probability1; consumption does not depend on acceptance. PixieDust: Levitation/Glowing100amp1. Ambrosia: Strength/Absorption/Jump/Luck3600amp2. Cannoli: Strength3600amp2. Three dragon-meat rice foods each Saturation100amp0 plus FireResistance2400amp0 (fire), Jump2400amp2 (ice), Speed2400amp2 (lightning). GhostCream Levitation400amp0; PixieMilkyTea Invisibility2400amp0. DelightFoodItem only adds a missing-mod tooltip; no combat callback disable if FarmersDelight absent. Status quantities, absorption capacity and nutrition remain native, no automatic extra Stage multiplier; ordinary buffed attacks already scale at native damage point. Acquisition/nutrition trivia excluded.

## Dragon flesh

Server DragonFlesh.finishUsingItem before parent consumption: Fire ignites consumer5seconds; Ice applies Slowness100amp2; other registered type Lightning spawns real LightningBolt at consumer with no setCause/visualOnly/loot tags. This can affect nearby recipients through native bolt tick, not just eater. Reuse R2g9a native fire/lightning semantics and single final hurt Stage points; do not manufacture ice damage or assume food bypasses effect resistance.

## Lightning armor

ServerEvents.onLivingHurt registered to Architectury LIVING_HURT; exact installed Architectury bridge handles NeoForge LivingIncomingDamageEvent and setsCanceled(true) on EventResult.isFalse. Exact four DragonsteelLightning armor slots reject exact DamageTypes.LIGHTNING_BOLT only, all Living recipients; not IS_LIGHTNING tag or iceandfire:dragon_lightning/mob_attack chain. Incoming cancellation blocks HP path but cannot retroactively undo Entity.thunderHit fire-timer changes or other bolt callbacks. This is a separate working binary admission hook from previously reviewed Uranus armor amount/absorption mismatch. No Stage on immunity.

## Ghost death delivery

Additional registered ServerEvents.onEntityDie (Architectury LivingDeathEvent bridge): server Player death, config ghost.fromPlayerDeaths (snapshot true), lastHurtByMob instanceof Player, random1/3, and significant-fall entry source FALL/DROWN/LAVA OR active Poison => creates Ghost at victim, finalizeSpawn(SPAWNER), addFreshEntity, then sets daytimeMode=true. No native target/fromChest assignment here; normal accepted Ghost AI decides later behavior. Snapshot is file evidence, not proof of the loaded runtime setting. It is a summon/control event, not a new damage source or scaling point. Preserve death cancellation/order and reuse Ghost damage packages.

## Exclusions

Jar/house capture and pet storage, texture/particle colors, food crafting, portal/progression and ordinary movement navigation excluded briefly. Native combat status, source identity, removal/admission and summon consequences above retained. No runtime boss/L2 test, Stage implementation or production change.

## TNO integration decisions

- **Persistent chain attachment and pull**: COMPOSITE, CUSTOM_ROUTED, ADMISSION_GATED, NO_STAGE_VALUE. Stage: no additional value; Direct movement/persistent UUID mechanics; no HP scalar.
- **Flute native flight interruption**: BINARY, CUSTOM_ROUTED, ADMISSION_GATED, NO_STAGE_VALUE. Stage: no additional value; Native recipient/owner/fallen state only.
- **Pixie native indirect_magic HP**: NUMERIC_SCALABLE, VANILLA_ROUTED, ADMISSION_GATED. Stage: yes; Once at PixieCharge.onHit native hurt5.
- **Pixie statuses, theft and hurt admission**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: no additional value; Statuses/item transfer and true-without-HP gate remain native.
- **Native Pixie healing**: NUMERIC_SCALABLE, VANILLA_ROUTED, ADMISSION_GATED. Stage: yes; Once at native Pixie heal5 request.
- **Combat food status support**: COMPOSITE, VANILLA_ROUTED, ADMISSION_GATED, NO_STAGE_VALUE. Stage: no additional value; Keep vanilla potion/nutrition/absorption resource quantities; downstream attacks scale once.
- **Dragon flesh native fire/lightning damage**: NUMERIC_SCALABLE, VANILLA_ROUTED, ADMISSION_GATED. Stage: yes; Once at native on_fire or thunderHit final hurt, reusing R2g9a points.
- **Full Lightning Dragonsteel native bolt immunity**: BINARY, VANILLA_ROUTED, ADMISSION_GATED, NO_STAGE_VALUE. Stage: no additional value; Exact damage type and four-slot IncomingDamage cancellation.
- **Conditional Ghost summon on Player death**: BINARY, CUSTOM_ROUTED, ADMISSION_GATED, NO_STAGE_VALUE. Stage: no additional value; Configured native summon; reuse Ghost attack Stage point.

[Machine-readable packages, native paths and future fixtures](iceandfire-r2g9b-control.json). Validation reproduces new witnesses, checks significant call order/amounts, preserves accepted records and prior evidence, runs five tooling tests and diff checks. No whole-mod completion claim.

Exact next task: R2g10: whole-Iaf-JAR combat/source closure and short exclusions, resolve any uncovered callbacks, deduplicate/promote Ice & Fire COMPLETE, run full validation/tests, push/live-verify; then Eternal Starlight if usage healthy.
