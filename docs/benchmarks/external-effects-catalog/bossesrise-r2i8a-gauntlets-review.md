# R2i8a — Bosses Rise Ice and Sandworm Gauntlet delivery

Ice and Sandworm Gauntlet native item prerequisites, costs, owner/control and hazard delivery; protected payloads reused.

Static review only. Future runtime fixtures remain unexecuted; whole Bosses’ Rise review is PARTIAL.

## Ice native use

IceGauntletItem extends ShieldItem, not plain Item. use starts animation then delegates ShieldItem.use, which starts actual item use and returns consume; inherited block animation/use duration72000 supplies charge/jump/holding admission. PlayerAnimationHandler only schedules cosmetic animation and does not substitute for startUsingItem. Native shield eligibility/directional block/source shield bypass and cooldown remain intact. Item durability1200; native mainhand modifiers attackDamage+4, attackSpeed-3, attackKnockback+2.5 are ordinary melee inputs, not extra HP callbacks or additional Stage points. Successful native melee weapon callback hurtEnemy calls super, writes target frozen400 regardless of the returned item boolean, then returns it. It does not invoke hurt, canFreeze or addEffect. Player.attack/ItemStack dispatch still controls whether the callback occurs. Frozen counter/Roll/native freeze immunity and later passive tick use protected R2i5b, not fabricated instant freezing damage.

## Ice wave

ServerPlayer release while secondary-use active and item cooldown absent computes held ticks i=72000-timeLeft; negative returns. Begins end animation, clips eye/view along blockInteractionRange*1.1 with COLLIDER/Fluid.NONE; MISS returns before cost. Pitch is clamped+/-85 only for wave direction after ray. Calls native iceWave range=min(i/32+.5,1.5)*12 (6..18), count=min(i,32), damage10,speed1, origin hit location. Cooldown80 and durability1 follow even if count0 or all candidate terrain rays reject. Protected helper places normal/cluster candidates, owner player, delays16+j, native stored damage10. No eye-to-each-spike LOS override or guaranteed count; normal versus cluster admitted HP/control/reload semantics remain R2i5b. Scale at later native spike/cluster hurt, never setDamage and hurt both.

## Ice leap

LivingJumpEvent only ServerPlayer actively using exact gauntlet and no gauntlet cooldown; requires attachment !active and no stored shard UUID. Sets active, costs10durability, stops use, starts jump animation, cooldown400, Spatial push(view+Y2). LivingFallEvent ServerPlayer calls onFall; true cancels fall. PlayerFlyableFallEvent calls it without cancellation. onFall needs ONLY active flag, not continued equipment/use/cooldown; clears flag, starts landing animation, native iceBurst range8/count40/damage3, cluster random1/10 OR index<4, cooldown200. It also independently scans playerBB.inflate2 for any Entity except self, owner-matched OwnableEntity, dead/spectator, normal spike or cluster. Requests ownerless freeze10 then writes frozen200 regardless of hurt result; no Living/canFreeze/team/LOS guard. Passive freeze eligibility remains separate. Falling after item swap or native saved active state is a genuine fixture. Landing HP10 and delayed spikes are separate native payloads; no duplicate Stage scaling.

## Ice shards

Native cluster interact with gauntlet and free random slot0..3 starts real use, stores UUID, replaces break resource with slot index, sets held and owner player. useOn searches cluster centers near clicked position in full-side3 box and delegates first successful interaction; client only predicts success. Post PlayerTick attachment clears UUIDs whose loaded entity is not Cluster. With at least one valid shard and continued exact gauntlet use, it can collect additional unheld clusters from full-side3x2x3 box one block ahead of eye until4 slots. It does not consume durability or apply a cooldown there. When no longer using that gauntlet, every>=2 game ticks releases the first valid stored cluster: new native IceSpikeProjectile owner player at eye, speed4, inaccuracy=slotIndex*5, baseDamage4, knockback8; then discards cluster, clears UUID and updates lastShot even if addFreshEntity failed. Projectiles preserve R2i5b swept indirect_magic ceil(speed*base) and genuine playerTouch FREEZE8 as different routes. No extra HP added by attachment. Held clusters can release held-state separately when player stops use; native tick ordering/removal matters. Attachment active/shard UUIDs/last_shot persist; missing entities clear naturally.

## Sandworm modes

SandwormGauntlet extends Item, durability1000, use duration72000/BOW. Crouching on top face in onItemUseFirst sets operation mode earthquake; ordinary use defaults missing mode to poison_barrage, applies its modifiers, starts using and consumes interaction. Earthquake adds MOVEMENT_SPEED and JUMP_STRENGTH negative-infinity ADD_VALUE modifiers keyed freeze, ANY equipment group. Poison mode adds MOVEMENT_SPEED +.5 ADD_MULTIPLIED_BASE under a key named slow: code is a positive base-speed modifier, do not infer a slow from its label. release or dropping clears operation mode and removes these two modifier IDs. Native attribute clamping/use lifecycle must be retained; they are control/resources with no Stage multiplier.

## Sandworm quake

Server onUseTick in earthquake mode: at useTick30 and every20 thereafter, first costs10 durability via native hurtAndBreak, then chooses up to4 random Living targets other than user in full-side28x8x28 box with strict3<distance<14. No explicit ally/LOS/creative/spectator predicate at candidate selection. Remaining positions use random horizontal radius[3,14). Four native spawnSandColumn attempts pass delay0 and owner user; protected terrain COLLIDER ray may reject each. Column actual victim admission still checks alive, virtual invulnerable, owner and alliance, with push before ally HP rejection. Normal owned payload indirect_magic5 direct column/causing user; unresolved owner magic5 remains native. Cost/count/delay are not Stage values; only final native column HP once.

## Sandworm barrage

On release in poison mode compute count=clamp(Java integer (useTick+4)/10,0,4), requiring>=1; earliest count1 at6 held ticks, then2/3/4 at16/26/36. Force=clamp(.5+(useTick-7)/5,.5,1), speed=force*1.5 (.75..1.5), inaccuracy8+count*5. Server directly constructs count PoisonSpitPr at eye with firing ItemStack, sets owner user, silent, baseDamage6 and knockback5, then calls inherited instance shoot along view. It does NOT call the static convenience helpers. No native barrage durability deduction or item cooldown in this method; item-use stat increments for Player. AbstractArrow native speed/base/enchantment HP, return-gated projectile knockback and independent impact PoisonArea use R2i6. Area has no owner transfer, so later native poison tick still has no attacker. Keep each stage point downstream; do not scale count or base6 in addition to HP.

## Correction and reuse

R2i6 boss payload/admission evidence remains valid. Its sentence that the Gauntlet uses a static shoot helper is superseded by this checkpoint: native constructor plus invokevirtual shooting is the real player path; invokestatic census has only convenience helpers calling each other inside PoisonSpitPrEntity. This is an additive, evidence-backed correction, not a rewrite of protected history. Existing nine hazard packages are extended with player delivery paths under the SAME IDs and same scaling points for final deduplication. Gauntlet input/control and landing pulse add three new packages. Native source tags, Resistance/Nullification/effect applicability and Roll semantics are reused unchanged. Cross-mod runtime results remain untested; origin/merge attribution for passive freeze and poison still requires design before Stage implementation.

## Excluded

IceGauntletMessage handles client sound/particles only, not HP, frozen counters or server input. Player animations, item tooltip/render transforms, mining swing suppression, UUID animation keys and repair acquisition are excluded after identifying genuine use/attack delivery. No runtime/Stage/production changes. Dragon armor, Undying Tentacle and Trident remain next equipment subsections.

- **Ice Spike native delayed freezing strike**: COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE, VANILLA_ROUTED. Stage: IceSpikeEntity lambda$baseTick final ownerless freeze stored-damage hurt argument.
- **Ice Cluster native delayed freezing strike**: COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE, VANILLA_ROUTED. Stage: IceSpikeClusterEntity lambda$baseTick final ownerless freeze stored-damage hurt argument.
- **Ice Spike native swept magic hit**: COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE, VANILLA_ROUTED. Stage: IceSpikeProjectileEntity.onHitEntity final ceil/clamp speed*baseDamage hurt argument.
- **Ice Spike native playerTouch freezing hit**: COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE, VANILLA_ROUTED. Stage: IceSpikeProjectileEntity.playerTouch final explicit FREEZE 8 hurt argument.
- **Native passive freezing from ice counters**: COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE, VANILLA_ROUTED. Stage: LivingEntity.aiStep final native freeze 1 hurt request with proven origin attribution, never counter and HP both.
- **Sandworm native sand column damage and push**: COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE. Stage: SandColumn.damageEntity native hurt5 after eligibility and with its resolved magic/indirect_magic source; only once.
- **Sandworm native spit arrow impact**: COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE. Stage: AbstractArrow final native arrow hurt amount after speed/base/enchantment calculation for genuine spit; never also scale baseDamage.
- **Sandworm poison applications and hazard admission**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: Native admission/resources, incoming modifier, scripted defeat, effect delivery or control; no additional scalable HP request here.
- **Sandworm-origin native poison HP ticks**: COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE. Stage: Native PoisonMobEffect hurt1 only with proven external-effect provenance and native HP>1 gate; no application/duration/amplifier scaling.
- **Ice Gauntlet native use, freezing counter, leap and shard resources**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: Native use/admission/control/resource or counter delivery; no additional outgoing HP multiplier here.
- **Ice Gauntlet native landing freezing pulse**: COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE. Stage: GauntletAttachment.onFall native ownerless freeze10 hurt argument only; not frozen counter or delayed spike damage.
- **Sandworm Gauntlet native modes, cost and movement modifiers**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: Native use/admission/control/resource or counter delivery; no additional outgoing HP multiplier here.

[Machine evidence, packages and native paths](bossesrise-r2i8a-gauntlets.json).

Exact next task: R2i8b: Undying Tentacle real item modes/Ghost Tentacle and Kraken Trident native special delivery; then Dragon armor procs/remaining weapons, watched-method closure and Bosses Rise final dedup/promotion. Apply the R2i8a additive Sandworm producer correction during promotion; protected prior evidence remains immutable.
