# R2i3a — Bosses Rise Knight defense and native mark

Underworld Knight native defense, stack/mark and phase admission only; offensive payloads remain next.

Static review only. Future runtime fixtures remain unexecuted; whole Bosses’ Rise review is PARTIAL.

## Native initialization

Constructor fields hpGate75/50/25=true; synced immuneStacks1, immuneMax1, undeadCinematic0, cinematicfalse, transformedfalse, introAttack10. createAttributes defaultsHP250/armor0/attack15/move.3/KBresistance1; finalizeSpawn overridesHP280/armor10/attack13 from native config defaults (actual server config may differ). Installed arena NBT explicitly contains Knight Health150,BossPhase-1,Stateidle,Timer5951,SpawnAnimtime0,UndeadCinematic0,HpGate50/25true but no HpGate75 or immune stack keys. Reader retains constructor stack defaults when keys absent; reads missing HpGate75 asfalse when BossPhase present. These are source/data initialization contracts, not measured final runtime HP. Native arena versus ordinary finalized spawn are distinct future fixtures.

## Admission order

hurt delegates processHurt(source,amount,false). If state dead OR source BYPASSES_INVULNERABILITY with raw health-amount STRICTLY<0, delegate directly to super.hurt before bespoke cinematic/source/stack gates. Otherwise cinematictrue returnsfalse even for fromMark and exactly-lethal bypass. flag=fromMark OR bypass tag. flag skips server/UndeadCinematic<=0/exact-type exclusions(IN_FIRE,FALL,LIGHTNING_BOLT,WITHER,WITHER_SKULL), and skips the isInvulnerable stack branch. Ordinary sources must satisfy those filters; then if stacks>0 (or underlying invulnerable) only stuck-state branch can proceed. Non-stuck ordinary hit returnsfalse. All delegated hits still face native Entity/LivingEntity admission, incoming events, armor, Resistance, absorption and iframes; no Tensura/L2 bypass is proposed.

## Stack vs hp

isInvulnerable returns stacks>0 OR base getter; removeOneImmuneStack simply subtracts1, no clamp. Ordinary admitted hit while state stuck removes one stack BEFORE hurt. If still invulnerable -> stagger; otherwise idle_to_knocked_down. Then super.hurt(source,min(20,amount*.1)) regardless eventual return. No positive-amount or successful-hurt requirement for stack removal in this branch. Therefore stack break and reduced HP attempt are distinct; a failed downstream hit can still consume a stack. Exact installed Entity.isInvulnerableTo checks backing invulnerable field rather than virtual isInvulnerable getter, so remaining Knight stacks do not by themselves cancel the delegated reduced hit. Source/event-based native rejection still applies. No second Stage scaling for .1 reduction/cap.

## Hp gates

Unshielded or flag-admitted branch computes proposed ratio=(raw currentHP-raw incoming amount)/MAX_HEALTH before native mitigation. The75% gate is outerif;50% then25% are in its else branch. Each enabled flag is cleared before super.hurt, even if downstream damage fails. Phase2 gate75/50/25 clamps crossing amount to max(amount-(threshold-proposedHP),1), chooses respective ranged pattern/index0 and jump_back. Phase2 50% additionally immuneMax2/stacks2; outsidephase2 50% setsstacks1. Phase0 75% can consume itsflag without entering latergates on samehit. Minimum1 is literal, not perfect post-mitigation HP lock. Never Stage-scale gates/ratios/cap or undo native pre-hurt state mutation.

## Stuck delivery

Server doAttack tracks light/heavy counts only while invulnerable; heavy/light-heavy incrementsheavy and setsisStuck if lightCounter>=3 OR heavyCounter>=(HP ratio>.5?3:5); non-LIGHT_ATTACK resetslight count after check. End of heavy/light-heavy enters stuck ifisStuck then resetscounts, else stuck_to_idle. setState(stuck) creates native scale1 mark before base state transition. Thus genuine stack-opening opportunities come from actual native attacks; no forced-state prototype authorized.

## Mark creation

Server placeMark discards existing first-passenger KnightMark, creates mark with random side offset, sets scale and ownerUUID to Knight, calls native startRiding(this) without force and ignores its result, then addFreshEntity. PositionRider uses mark stored world-axis offset. Actual producers: stuck(scale1); heavy/light-heavy timer5(scale.5); combo1 derived attackAnimtime60 whenheavy below3/5; combo2 timer115 same threshold(scale.5); vertical ranged timer1 at patternIndex3(scale1). Scale affects lifetime/visuals, not hurt multiplier. baseTick server discards when ownerUUIDnull or tickCount>(int)(100*scale), normally50/100; unresolved nonnullUUID alone does not immediate-discard.

## Mark hit

KnightMark.hurt server with nullUUID discards and returnstrue. With resolved Living owner: multiply incomingamount by2. Knight owner and doubledamount>4 -> removeone stack only ifpositive, setState(knocked_down) even ifno stacks; then processHurt(originalsource,doubledamount,true), IGNORE result. Doubledamount<=4 still forwards with fromMarktrue but no forcedknockdown/stackloss. OtherLiving owner gets hurt(same source,doubledamount), resultignored. Mark then discards and returnstrue independently of owner HP success. Missing/nonliving owner delegates Entity.hurt; client returns true. Thus incoming>2 can break stack independently of HP, and low hits can bypass bespoke stack filter without breaking stack. No attackertype/projectile/melee exclusion exists here. fromMark does NOT skip cinematic or native fire/armor/Resistance/event checks. Stage belongs only to original admitted attack amount once; marker forwarding/native×2 receives no additional multiplier.

## Phases and death

R2i2b legacy post-HP/pre-Post .1 restoration calls Knight shouldCancelDeath. State dead returns !isTimerDone; otherwise phase0 ->phase1/stacks1/fake_dead; phase1 returns true; phase2 ->RANGED_0/index0/jump_back/phase3/stacks1; phase3 ->dead. Shared bypass-invulnerability skips restoration. Fake_dead duration85 then requires nearestPlayer within20 before resurrect, returns home ifpresent and setscinematictrue. Resurrect timer160 sets transformed; duration440 completion clearscinematic, phase2, resetsall HP gates, stacks1, setHealth(MAX_HEALTH), idle. This is native resurrection/reset, no heal scaling. Phase3 revenge completion stacks0/revenge_knocked_down(duration700); itscompletion returnsphase2/stacks1. Dead duration155 completion requests native self999 player_attack only if getSourceEntity isPlayer, otherwise fell_out_of_world; actualhurt result is not used. Preserve source/admission and scripted defeat, no Stage multiplier on999.

## Timing and intro

Base setState resets timer to-3 when nonzero; timer increments each tick and isTimerDone uses strictly>duration. Server concrete tick skips state payloads while transitioning. Arena phase-1 idle plus Player in32x16x32box centeredY+8 starts intro and cinematictrue; duration377 completion clearscinematic, setsphase0/idle. Old baseTick->procedure->onSpawn(226) is genuinely called but requires positive SpawnAnimtime. Native default and installedarena both0; census has no active positive native setter, only deserialization/decrement. Treat shared R2i2b knight_spawn as dormant conditional legacy route, not a demonstrated arena-delivered HP reset/teleport. Do not synthesize positiveNBT merely to produce a test. Cinematic cleanup discards nearbySoulSkeleton/SoulKnightWitherSkeleton inBBinflate64; cosmetic camera details excluded.

## Traits and persistence

Knight fireImmune=true (also builderfireImmune), canFreeze=false, isPushable=false, nativeKBresistance1. canBeSeenAsEnemy returns canBeSeenByAnyone instead of hiding because stackgetter istrue; native target/event criteria remain. Exact-type FALL/LIGHTNING/WITHER exclusions are bespoke and flag-skippable, while nativefiretag immunity still applies downstream. Storedstack/gate/counter/state/phase persistence preserved. KnightMark writes UUID key Owner but reads owner; normal roundtrip cannot restore that UUID, so server mark disposal follows nullUUID. Knight attackpattern save also reverses key/value (attackname -> AttackN), reader expects AttackN ->name; retained as distinct reload coverage, no repair. No claim that runtime event listeners or data fixes have been tested.

## Tno decision

Five defense/control packages, none creates an independently scalable numeric payload. Native reductions/doubling affect the incoming attack once; do not multiply original attack and forwarding again. Separately test stackcount change, state transition, hurtboolean, HP change and source identity. Runtime remains NOT_RUN; no production/Stage/L2/Phase6/7 changes. Offensive tick branches are witnessed for state context but NOT yet semantically complete.

- **Knight stack resource and hurt admission**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: Native defense/resource/phase or incoming-attack modifier; no additional Stage multiplier.
- **Knight native weak-point mark forwarding**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: Native defense/resource/phase or incoming-attack modifier; no additional Stage multiplier.
- **Knight native HP-triggered state gates**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: Native defense/resource/phase or incoming-attack modifier; no additional Stage multiplier.
- **Knight cinematic/resurrection/revenge/death control**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: Native defense/resource/phase or incoming-attack modifier; no additional Stage multiplier.
- **Knight native combat defenses and visibility**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: Native defense/resource/phase or incoming-attack modifier; no additional Stage multiplier.

[Machine evidence, packages and native paths](bossesrise-r2i3a-knight-defense.json).

Exact next task: R2i3b: Underworld Knight offensive payloads only: actual server melee states/attackCombo1 ring, SwordWave horizontal/vertical sources, jumpSlash SoulShockwave, revenge Rift/BigRift and legitimate soul-skeleton summon deliveries/defenses. Reuse completed R2i3a stack/mark/phase defense and R2i2b helpers; do not repeat them. Then Infernal Dragon, Yeti, Sandworm, Kraken and equipment. Static only.
