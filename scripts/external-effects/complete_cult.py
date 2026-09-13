"""Audited Cult-only semantic assembly, continuing the protected 29-record draft.

No Minecraft execution. Historical drafts/evidence are immutable inputs.
"""
from catalog_common import *
from collections import Counter
import copy
import re
from assemble_batch import refresh

CHECKPOINT='R2c3-complete'
START='a65d652571578156c93a78986ef4a28ae895113d'
D=read_json(OUT/'partial-drafts/cultofazazel-r2c3-partial.json')
E=copy.deepcopy(D['effects']); P=copy.deepcopy(D['paths'])
NATIVE=['native-evidence/cultofazazel-partial.json','native-evidence/cultofazazel-r2c1.json','native-evidence/cultofazazel-r2c2.json','native-evidence/cult-completion.json','native-evidence/cult-final.json']
W={w['id']:(f,w) for f in NATIVE for w in read_json(OUT/f)['witnesses']}
REFS=['vanilla-evidence/cult-completion.json','vanilla-evidence/cult-final.json','vanilla-evidence/variants-prerequisites.json','vanilla-evidence/vv-completion.json','reference-evidence/cult-loader-244.json','reference-evidence/cult-final-244.json','reference-evidence/vv-loader-244.json']

def get(key):return next(e for e in E if e['id']=='cultofazazel:'+key)
def proofs(ids):
    return [dict(evidence_file=W[k][0],witness_id=k,entry=W[k][1]['entry'],methods=[m['name'] for m in W[k][1].get('methods',[])]) for k in ids]
def component(name,formula,relation='CUSTOM',numbers=None,binary=None):
    return dict(primitive=name,formula=formula,vanilla_relation=relation,numerical_parameters=numbers or {},binary_parameters=binary or [])
def add(key,name,kind,behavior,ids,closest,similar,difference,components,*,numbers=None,state=None,registry=None,damage=None,eligibility=None):
    row=dict(id='cultofazazel:'+key,mod_key='cultofazazel',display_name=name,registry_ids=registry or [],primary_classification=kind,
        actual_behavior=behavior,human_summary=behavior,implementation=proofs(ids),closest_vanilla_equivalent=closest,
        vanilla_similarities=similar,vanilla_differences=difference,components=components,numerical_parameters=numbers or {},
        custom_state=state or 'No custom target data; ordinary native state only.',
        eligibility=eligibility or behavior,damage_path=dict(source_mod_custom_damage_type=False,types=damage or []),
        delivery_paths=[],primary_test_source=None,alternate_sources=[])
    E.append(row);return row
def path(key,rows,labels,source,setup,ids):
    pid='cultofazazel:'+key
    P.append(dict(id=pid,mod_key='cultofazazel',status='VERIFIED',labels=labels,effect_ids=[e['id'] for e in rows],primary_source=source,setup=setup,implementation=proofs(ids)))
    for e in rows:
        e['delivery_paths'].append(pid)
        if not e['primary_test_source']:e['primary_test_source']=source
        elif source!=e['primary_test_source'] and source not in e['alternate_sources']:e['alternate_sources'].append(source)
    return pid

# Finalize the earlier draft's package boundaries. Keep former shared observations
# as context, not duplicated assertions that every component belongs to every row.
for e in E:e['source_context']=e['actual_behavior']
scoped={
 'azazel_shield':'Server hurt rejects IN_WALL and states2,7..10. Otherwise a LivingEntity source owner increments hitCounter before super.hurt success; reaching the inclusive sorted configured threshold5..20 in idle state0 resets counter/threshold, enters shield state2 for100 entity ticks and requests heal20. The triggering hit still delegates to super. Later state2 hits return false. Its separate pre-mitigation terminal threshold is recorded in azazel_terminal.',
 'azazel_terminal':'Before normal super.hurt, currentHP-rawIncomingAmount<=0.05*maxHP starts death cinematic state9 and returns false. This does not subtract HP. At state9 tick200 native loot/barrel creation and discard remove the boss. The audiovisual explosion does not damage entities. Attack state/timer are not persisted by the shown save override.',
 'azazel_wind':'State1 countdown60: each active entity-tick call adds (0.8*normalizedAway.x,0.2,0.8*normalizedAway.z) to Players in AABB20. At timer30 requests mobAttack5. Motion does not depend on hurt success; no explicit creative/spectator/LOS filter.',
 'azazel_pull':'State11 countdown60: while timer>15 add horizontal normalizedToward*0.6 to Players in AABB20. At timer15 set vertical velocity1.5 and request mobAttack5. Velocity is independent of hurt success; no explicit creative/spectator/LOS filter.',
 'azazel_launch':'State12 countdown80: at timer40 Players in AABB5 receive mobAttack8 request and absolute vertical velocity2.5, independent of hurt success. Explosion particles/sound have no Explosion damage call.',
 'azazel_wheel':'State3 countdown90: timer<=50 with target sets boss horizontal normalizedToward*1.2. Every third entity tick Players in boss AABB1 receive mobAttack4 request and full normalized dashVector*1.5 (including Y), independent of hurt success.',
 'midas_fire_ring':'State13 countdown120: elapsed=120-timer; expanding radius=elapsed/120*30. Players in AABB35 whose absolute(3D distance-radius)<=1.5 receive inFire8 request and igniteForSeconds5 independently of hurt success. No explicit creative/spectator filter.',
 'midas_inventory':'During Midas state13, Player distance<=6 in AABB35 increments UUID counter. At configured40 calls choose uniformly among nonempty non-RAW_GOLD slots across36 main+4 armor+1 offhand; replace the whole stack with fresh RAW_GOLD of the old count. Item/components are lost. Outside6 but inside35 resets counter; outside the scan does not. Threshold resets even if no eligible slot. Tracker resets at attack start and is not saved. Curios, ender chest, cursor and nested inventories are not inspected.',
 'native_fangs':'Azazel arrow-attack variant1 creates20 EvokerFangs at each countdown100/80/60, target x/z offsets[-1,1), warmup0, ownerAzazel. Native tick damages at warmup-8: live non-invulnerable recipient, not owner, not allied. Owner-present indirect_magic request6; ordinary ownerless factory uses magic6, but Cult supplies the owner. Successful hurt alone enables native enchantment post-attack callback. No reset of invulnerableTime.',
 'believer_protection':'Azazel Pray state5 countdown180 calls setProtected150 on Believers in AABB40. Protected Believer.hurt returns false before superclass; server entity tick decrements/clears protectedTimer. No damage threshold or vanilla Resistance modifier.',
 'believer_sickness':'Server gunpowder interaction sets IS_SICK; golden apple clears it, consuming one unless creative. Sick OR praying stops navigation and invokes travel(Vec3.ZERO); this is not a vanilla poison/slowness effect and does not gate boss healing. Doctor first attempts after initial1200 decrement ticks plus the zero-branch tick; later attempts every2401 ticks choose one healthy Believer in AABB15. Doctor refuses a potion trade if a sick Believer is in AABB10. Doctor sicknessTimer is saved.',
 'believer_healing':'Every20 Believer entity ticks retain current live Azazel only at distanceSquared<1600, otherwise find first in AABB30. Selected live boss receives heal5 every20 ticks. No aggro, sickness, praying or protected-state gate. Native heal event and max HP cap apply.',
 'bad_omen':'Believer server die callback, before super.die, gives a Player source owner actual BAD_OMEN36000/0 and spawns a Statue. Cult Azazel checks actual BAD_OMEN on nearby Players in AABB30 to initiate aggro. Literal holder also retains native per-tick nonspectator ServerPlayer/nonpeaceful village and eligible-raid conversion to RAID_OMEN600/same amplifier; not an empty ZoneEffect.',
 'guardian_rapid_melee':'Native combo entry distanceSquared<=16. performMeleeAttack uses distanceSquared<=16/64 unbuffed/buffed, clears target.invulnerableTime then requests mobAttack3/8. Other damage admission remains. Combo3..5 sets of three attempts at goal countdown10,6,2:9..15 attempts. Normal non-every-tick goal cadence is two server ticks:8 ticks between attempts within a set,22 ticks per countdown11 set. Interruption/AI state can pause scheduling; no fixed DPS claim.',
 'guardian_mega_punch':'Goal may enter special when16<distanceSquared<=100, special cooldown0 and random1/20. State5 goal countdown40 calls mega-punch at30 and resets cooldown160 goal invocations (normally320 server ticks while goal runs). Native Player/other LivingEntity scan AABB10/20 plus squared radius100/400, excludes self/Welcomer/Manipulator/Believer/Guardian/StatueBossunit/Statue/Azazel. Requests mobAttack10/15 and adds Y0.9 independently of hurt success. Does not clear invulnerableTime.',
 'welcomer_buff':'Every10 Welcomer entity ticks IS_CASTING reflects whether a Guardian with a target exists in AABB30. Every10 Guardian ticks IS_BUFFED reflects a nearby casting Welcomer. Boolean switches rapid damage3->8 and squared range16->64; mega damage10->15 and radius10->20. Multiple Welcomers do not stack. No Strength effect/attribute modifier. Guardian death WEAKNESS sound applies no Weakness effect.',
 'golem_launch':'After successful parent IronGolem.doHurtTarget, Cult adds velocityY0.4. Parent already adds0.4*max(0,1-KR), so total added Y=0.4*max(0,1-KR)+0.4. Both parts require parent hurt success; extra0.4 ignores KR. Native ordinary base attack damage randomization is inherited.',
}
for key,text in scoped.items():get(key)['actual_behavior']=text
get('golem_healing_pull')['actual_behavior']=get('golem_healing_pull')['actual_behavior'].split(' Separate successful super')[0]+' CreatorUUID and IsHealingPhase are saved. Believer-attacker targeting is source context, not an extra damage mechanic.'

# Continue after Gilded Golem. Literal holders stay individual; producer packages
# retain their distinct admission paths without claiming ownership of vanilla code.
holders={
 'wither':('Wither','1 wither damage every max(1,40>>amplifier) ticks; unlike Poison it has no HP>1 floor.',{'base_interval':40,'requested_damage':1},['minecraft:wither']),
 'slowness':('Slowness','Movement-speed ADD_MULTIPLIED_TOTAL -0.15*(amplifier+1).',{'modifier_per_level':-.15},[]),
 'poison':('Poison','1 damage only while HP>1, interval max(1,25>>amplifier). Raw magic source; installed NeoForge poison holder with magic fallback.',{'base_interval':25,'requested_damage':1,'HP_floor':1},['neoforge:poison','minecraft:magic (fallback/raw)']),
 'unluck':('Unluck','Luck ADD_VALUE -(amplifier+1); no direct damage or attack-speed effect.',{'modifier_per_level':-1},[]),
 'darkness':('Darkness','Native holder and 22-tick fade factor; fog distance lerps toward15, terrain near=0.75*far, sky near0. Amplifier is not used by the pinned fog function.',{'fog_target':15,'blend_ticks':22},[]),
}
for key,(name,formula,nums,damage) in holders.items():
    add(key,name,'VANILLA_DIRECT',formula+' Bossunit supplies400 ticks/amplifier0..2; holder admission/merging/tick/cure are native.',
        ['coa2-bossunit'],'Minecraft1.21.1 '+name,'Uses the actual vanilla MobEffect holder and implementation.','External producer, not a different formula.',
        [component('MOB_EFFECT_'+key.upper(),formula,'VANILLA_DIRECT',nums,['native effect admission','native merging/expiration'])],numbers=dict(nums,bossunit_duration=400,bossunit_max_amplifier=2),registry=['minecraft:'+key],damage=damage)
bossrows=[get(k) for k in holders]
path('bossunit_random_holder',bossrows,['MOB_ATTACK','PASSIVE_AURA'],'netherman:statue_bossunit','Initial saved attackTimer300; when<=0 scan Players AABB20. Independently select ONE of five holders per Player, duration400 amp0..2. Reset200 if nonempty,20 if empty. No LOS/creative/hurt-success gate. Azazel passive and Midas summons use the same class.', ['coa2-bossunit','coa2-azazel'])
path('owned_skeleton_wither',[get('wither')],['SUMMONED_ATTACK','MELEE'],'Stick-owned minecraft:wither_skeleton','Sneak-use Manipulator Stick produces five with SummonerUUID and target filters. Successful native WitherSkeleton parent melee against LivingEntity addsWITHER200/0. Native effect implementation is WitherMobEffect, not the stick.', ['coa-stick','coa-stick-events'])
path('manipulator_skeleton_wither',[get('wither')],['SUMMONED_ATTACK','MELEE'],'Manipulator-produced minecraft:wither_skeleton','Manipulator summons1..2 with current target/gold equipment/drop0 and no SummonerUUID; successful inherited melee addsWITHER200/0. Preserve this ownership/admission difference.', ['coa3-entity/ManipulatorEntity'])
get('wither')['numerical_parameters'].update(skeleton_duration=200,skeleton_amplifier=0)

statue=add('statue_observation','Statue observation lock','CUSTOM_CONTROL',
 'Alive nonspectator Player eye distance<64, look dot>0.1 and LOS sets custom frozen state. Transition stops navigation/resets hasAttacked; while watched horizontal velocity becomes0 while Y remains. Unobserved releases. Custom attack goal runs only !frozen&&!hasAttacked, then marks one attempt even if hurt fails.',
 ['coa2-statue','coa2-statue-goal'],'Vanilla navigation stop/velocity assignment','Uses native LOS, look vector and navigation.','Custom watcher/one-attempt state; never frozenTicks, frost slowing or freeze DOT.',
 [component('AI_OBSERVATION_LOCK','visible observer => horizontal velocity0 and no attack goal',numbers={'distance':64,'dot_threshold':.1},binary=['alive nonspectator observer','LOS']),component('ATTACK_ATTEMPT_LATCH','one attempt between watch/release resets',binary=['hurt return does not gate latch'])],state='Synchronized custom isFrozen and hasAttacked state; inspect native save overrides, not a MobEffect timer.',registry=['netherman:statue_entity'])
path('statue_watch',[statue],['MOB_ATTACK','OTHER'],'netherman:statue_entity','Observe, break LOS/look away, allow attack attempt, observe again. Azazel passive summons and Believer-death creation use same implementation.', ['coa2-statue','coa2-statue-goal','coa2-azazel','coa2-believer'])
prisoner=add('prisoner_conversion','Prisoner capture and release','CUSTOM_CONTROL',
 'Manipulator chooses first Villager in AABB10, otherwise Piglin, otherwise Ghastly. Noncasting conversion start sets35; native normal alternating goal schedule reaches cast1 about34 server ticks later. Villager/Piglin branches create fresh prisoner with position and numeric MasterId, then discard original even if creation fails. Prisoner stops navigation, follows live master beyond distanceSquared25; ore-adjacent mining is animation only. Missing/dead master enters release state2 timer20, state3 waits Player within3, state4 timer10/reward, state5 timer15/fresh vanilla entity and discard. Zero-branch structure makes waits21/11/16 ticks. Only MasterId/PrisonState saved, actionTimer omitted; numeric ID relinking after reload is not guaranteed.',
 ['coa2-manipulator-convert','coa3-entity/ManipulatorEntity','coa3-entity/VillagerPrisonerEntity','coa3-entity/PiglinPrisonerEntity'],'Vanilla entity conversion','Creates/discards native entities and uses navigation.','Not convertTo: fresh output, no original HP/effects/equipment/trade copy, custom captive/release states.',
 [component('ENTITY_REPLACEMENT','fresh prisoner then fresh vanilla entity on release',binary=['original discarded','numeric master ID']),component('AI_CAPTIVITY','follow master beyond squared25; absent master waits for Player within3',numbers={'follow_distance_squared':25,'release_player_range':3}),component('RELEASE_STATE_MACHINE','20/10/15 countdowns plus separate zero branches',numbers={'cast':35,'release_timers':[20,10,15]},binary=['goal uninterrupted','master absent/dead'])],state='MasterId, PrisonState saved; actionTimer not saved.',registry=['netherman:villager_prisoner','netherman:piglin_prisoner'])
for key,entity in [('villager','Villager'),('piglin','Piglin')]:
 path(key+'_capture_release',[prisoner],['SPELL','MOB_ATTACK'],'netherman:manipulator + minecraft:'+key,'Legitimate '+entity+' conversion and native prisoner release. Preserve separate concrete recipient/output classes.', ['coa2-manipulator-convert','coa3-entity/'+entity+'PrisonerEntity'])
death=add('ghastly_direct_death','Manipulator Ghastly death branch','CUSTOM_DAMAGE','The cast1 Ghastly branch setsHealth0 then invokes die(magic). There is no hurt request, armor/resistance calculation or Player-recipient branch. Native die and its cancellable event remain; a death-event cancellation does not retroactively undo the preceding HP write.',
 ['coa2-manipulator-convert'],'Native death dispatch','Uses native setHealth/die and magic factory.','Direct HP assignment before death dispatch, not normal damage admission.',[component('DIRECT_HP_WRITE','setHealth(0)',numbers={'HP':0},binary=['Ghastly recipient']),component('DEATH_DISPATCH','die(magic) after HP assignment',binary=['native death event may cancel'])],damage=['minecraft:magic (death dispatch only)'])
path('ghastly_conversion_death',[death],['SPELL','MOB_ATTACK'],'netherman:manipulator + netherman:ghastly','No earlier Villager/Piglin candidate in AABB10; uninterrupted native cast reaches1.', ['coa2-manipulator-convert'])

honey=add('crimson_honey_bounce','Crimson Honey bounce','VANILLA_LIKE_EXTENDED',
 'fallOn requests causeFallDamage(distance,0,FALL), even when bounce-suppressed. Landing with negative Y and !suppressingBounce replaces velocity(-8dx,-2dy,-8dz). Side contact with entity.minY<blockY+0.9 and abs(dx)>.05 or abs(dz)>.05 replaces(-4dx,0.6,-4dz), unless bounce suppressed. No hurt-return gate.',
 ['coa2-honey'],'Vanilla SlimeBlock bounce and HoneyBlock contact','Uses fall callback and native velocity assignment.','Slime vertical factor1 living/0.8 other and no horizontal reversal; vanilla Honey uses different slide/fall formulas. Cult extends/inverts motion and removes fall multiplier.',
 [component('FALL_MULTIPLIER','causeFallDamage(distance,0,FALL)','VANILLA_LIKE_EXTENDED',{'multiplier':0}),component('BOUNCE_VECTOR','landing(-8dx,-2dy,-8dz); side(-4dx,.6,-4dz)',numbers={'landing_horizontal':-8,'landing_vertical':-2,'side_horizontal':-4,'side_vertical':.6,'side_threshold':.05},binary=['bounce not suppressed','landing Y<0 or side-contact predicate'])],registry=['netherman:crimson_honey_block'],damage=['minecraft:fall (multiplier0)'])
path('crimson_honey_landing',[honey],['ENVIRONMENT'],'netherman:crimson_honey_block','Native landing/fall callbacks; test bounce suppression separately.', ['coa2-honey'])
path('crimson_honey_side',[honey],['ENVIRONMENT'],'netherman:crimson_honey_block','Native entityInside horizontal-motion condition.', ['coa2-honey'])
sticky=add('honey_properties','Copied Honey movement/jump factors','VANILLA_DIRECT','Crimson Honey and EyeBlock copy vanilla Honey speedFactor0.4 and jumpFactor0.5. Native block-underfoot predicates apply these properties; EyeBlock does not inherit HoneyBlock side-sliding or Crimson Honey bounce.',
 ['coa3-NetherExp','coa2-eye','coa2-honey'],'Vanilla HoneyBlock speed/jump properties','Literal copied native coefficients and Entity queries.','Different blocks and shapes; extra Crimson Honey bounce is separately recorded.',[component('BLOCK_SPEED_FACTOR','native block-speed factor0.4','VANILLA_DIRECT',{'factor':.4}),component('BLOCK_JUMP_FACTOR','native block-jump factor0.5','VANILLA_DIRECT',{'factor':.5})],registry=['netherman:crimson_honey_block','netherman:eye_block'],numbers={'speed_factor':.4,'jump_factor':.5})
for key in ['crimson_honey_block','eye']:
 path(key+'_properties',[sticky],['ENVIRONMENT'],'netherman:'+('eye_block' if key=='eye' else key),'Native movement/jump while supported by this concrete block. Distinct geometry/contact setup; same inherited factor implementation.', ['coa3-NetherExp','coa2-eye','coa2-honey'])
void=add('void_contact','Void contact damage','VANILLA_DIRECT','The three ordinary Void blocks call server LivingEntity.hurt(magic,5); native damage processing remains. Each then independently adds Darkness60/0 even if hurt fails. Nether-suffixed variants omit this callback. Darkness is linked as its own literal-holder record.',
 ['coa2-void-corner','coa2-void-mid','coa2-void-midcorner'],'Vanilla magic damage','Actual native magic factory/hurt request.','New environmental producer and5 request; no custom damage identity.',[component('NATIVE_MAGIC_DAMAGE','hurt(magic,5)','VANILLA_DIRECT',{'requested_damage':5},['server LivingEntity'])],damage=['minecraft:magic'],registry=['netherman:void_corner','netherman:void_mid','netherman:void_midcorner'])
path('void_contact',[void,get('darkness')],['ENVIRONMENT'],'netherman:void_corner','Alternate void_mid and void_midcorner have the same entityInside instructions/empty collision semantics; all actual classes retained in witnesses. Contact: magic5 then Darkness60/0 independently.', ['coa2-void-corner','coa2-void-mid','coa2-void-midcorner'])
get('darkness')['numerical_parameters'].update(void_duration=60,void_amplifier=0)
point=add('pointed_blackstone_fall','Pointed Blackstone tip fall','VANILLA_DIRECT','Inherited PointedDripstone fallOn checks UP-facing TIP shape and calls causeFallDamage(distance+2,2,stalagmite). Custom support update destroys unsupported chains as drops. Native falling-stalactite spawning checks literal vanilla PointedDripstone, so this is not a Cult falling-stalactite damage source.',
 ['coa2-pointed','coa3-NetherExp'],'Vanilla upward Pointed Dripstone','Inherited tip predicate/fall-distance adjustment/multiplier/source.','Custom block identity and support chain; no legitimate falling-stalactite producer.',[component('TIP_FALL_DAMAGE','native causeFallDamage(distance+2,2,STALAGMITE)','VANILLA_DIRECT',{'distance_added':2,'multiplier':2},['UP','TIP','native fall admission'])],registry=['netherman:pointed_blackstone'],damage=['minecraft:stalagmite'])
path('pointed_tip_fall',[point],['ENVIRONMENT'],'netherman:pointed_blackstone','Land on an upward TIP; native fall immunity/effect reductions apply.', ['coa2-pointed','coa3-NetherExp'])

for key,classname,pause,geometry in [('crimson_web','CrimsonWebBlock',50,'oriented thickness2/16; stage0 full16x16, stage1 12x12, stage2 6x6'),('entrance','EntranceBlock',100,'stage0 cube16, stage1 cube12, stage2 cube6, centered')]:
 row=add(key+'_opening',classname.replace('Block','')+' opening wave','CUSTOM_CONTROL',
  'Native item-free interaction at stage0 BFS connected same blocks in six directions; loop continues while queue nonempty and size<1000 (outer bound, not a hard final-node cap). Scheduled delay=max(1,int(distance^0.8*3)). Stages0->1->2->3 every3 ticks, open hold'+str(pause)+' ticks then3->2->1->0 every3. Geometry: '+geometry+'; stage3 empty. Properties copy NETHER_WART_BLOCK, hasCollision=true; noOcclusion does not clear it, so inherited getCollisionShape follows getShape. Does not use WebBlock.entityInside/cobweb slowing.',
  ['coa3-block/'+classname,'coa3-NetherExp'],'Vanilla opening door/trapdoor terrain collision','Uses native scheduled block ticks, state and collision.','Custom connected wave and staged geometry; no effect, stun, or vanilla cobweb slowdown.',
  [component('TERRAIN_COLLISION','native collision shape follows stages0..3',binary=['hasCollision true','stage3 empty']),component('BLOCK_WAVE_TIMER','delay=max(1,int(distance^.8*3)); hold then reverse',numbers={'exponent':.8,'delay_factor':3,'step_ticks':3,'open_ticks':pause,'outer_search_bound':1000})],state='Blockstate stage and closing; scheduled ticks owned by world.',registry=['netherman:'+key],numbers={'open_ticks':pause,'step_ticks':3})
 path(key+'_interaction',[row],['ENVIRONMENT','ACTIVE_ITEM'],'netherman:'+key,'Native useWithoutItem on closed stage0 connected layout; shape cannot be inferred from appearance alone.', ['coa3-block/'+classname,'coa3-NetherExp'])
trap=add('traphive_wave','Traphive contact/projectile gate','CUSTOM_CONTROL',
 'Closed/nonwaiting server block entity accumulates contactTimer when any alive Player box intersects block AABB inflated0.05; reaches10 triggers wave, absent contact decrements1. Projectile block hit is a second trigger; ordinary right-click PASS. Connected same-block BFS outer size<1000. Per block delay=int(distance^.8*3); opening20, open hold100+int((maxDistance-distance)^.8*3), closing20. OPEN true from opening start until closing finishes. NETHER_WART_BLOCK copied hasCollision=true, full-cube closed/empty open. No hurt or effect call.',
 ['coa3-block/TraphiveBlock','coa2-traphive','coa3-NetherExp'],'Vanilla pressure/interaction-controlled terrain gates','Native OPEN state, collision, entity/projectile callbacks.','Custom buildup, connected wave and timers; no damage/debuff.',
 [component('CONTACT_COUNTER','present+1, absent-1, threshold10',numbers={'threshold':10,'AABB_inflate':.05},binary=['alive Player']),component('WAVE_GATE','OPEN during opening/open/closing until close completes',numbers={'transition_ticks':20,'base_open':100,'delay_exponent':.8,'delay_factor':3})],state='BlockStateAnim, Waiting, DelayTimer, AnimTimer, AutoClose, ContactTimer saved.',registry=['netherman:traphive'])
path('traphive_contact',[trap],['ENVIRONMENT'],'netherman:traphive','Legitimate Player contact buildup while closed; no creative exclusion in producer.', ['coa2-traphive','coa3-block/TraphiveBlock'])
path('traphive_projectile',[trap],['PROJECTILE','ENVIRONMENT'],'netherman:traphive + native projectile','Native block impact with closed gate; retain projectile impact event admission.', ['coa3-block/TraphiveBlock','coa2-traphive'])
door=add('grand_door','Grand Door collision and aim movement','CUSTOM_CONTROL',
 'Closed interaction opens temporarily:60 opening ticks,1200 open-countdown plus following zero-branch tick,40 closing ticks. Guardian/tamed-Ghastly sequence toggles permanent open/closed and sets bossCooldown36000. OPEN true in states1/2, false in3/0; main and matching parts over6x12 are updated. While opening/closing client Player distanceSquared<=400 receives independent yaw/pitch random[-.5,.5)*(1-distanceSquared/400)*5.5 each tick. Real rotations, not just particles. Placement requires replaceable6x12 area; parts forward use to main. Prison parts lacking a main do not independently run this block-entity aim callback.',
 ['coa3-block/GrandDoorBlock','coa3-block/GrandDoorPartBlock','coa3-block/entity/GrandDoorBlockEntity','coa2-guardian-goal'],'Vanilla doors and entity rotation','Native block collision and Player rotations.','Custom multi-block/timed gate with continuous actual aim disturbance; no potion effect.',
 [component('MULTIBLOCK_GATE','OPEN true in1/2, false in3/0',numbers={'width':6,'height':12,'opening':60,'open_timer':1200,'closing':40,'boss_cooldown':36000}),component('AIM_MUTATION','each angle += independent random[-.5,.5)*(1-distSquared/400)*5.5',numbers={'squared_range':400,'intensity':5.5},binary=['client local Player','opening/closing'])],state='DoorState, AnimTimer, AutoClose, Permanent, BossCooldown saved.',registry=['netherman:grand_door','netherman:grand_door_part'])
path('grand_door_use',[door],['ENVIRONMENT','ACTIVE_ITEM'],'netherman:grand_door','Main block or valid part forwarding normal use; temporary opening.', ['coa3-block/GrandDoorBlock','coa3-block/GrandDoorPartBlock','coa3-block/entity/GrandDoorBlockEntity'])
path('grand_door_guardian',[door],['MOB_ATTACK','ENVIRONMENT'],'netherman:guardian + tamed netherman:ghastly + grand_door','Native Guardian welcoming/roar state machine chooses usable door and invokes permanent toggles at its native sequence phases; retain cooldown and nearby actor prerequisites.', ['coa2-guardian-goal','coa3-block/entity/GrandDoorBlockEntity'])
fog=add('mansion_fog','Mansion view-distance fog','VANILLA_LIKE_EXTENDED','Server Player structure check every20 ticks sends inside-mansion_nether flag; client progress clamped0..1 changes0.01 each client tick. RenderFog lerps incoming near/far distances toward12/48 by progress and cancels fog event; color separately lerps toward(.6,0,.02). It limits rendered view distance, not AI LOS or HP. Separate from ZoneEffect.',
 ['coa3-event/MansionCheckHandler','coa3-client/ClientFogHandler','coa3-network/FogSyncS2CPacket','coa3-network/ClientPayloadHandler'],'Vanilla Blindness/Darkness fog','Uses fog near/far visibility distances.','Custom structure-driven12/48 interpolation, unlike Blindness5 or Darkness15; not a MobEffect and no shared cure.',
 [component('VIEW_DISTANCE','near/far=lerp(progress,incoming,12/48)',numbers={'near':12,'far':48,'progress_step':.01,'server_check_ticks':20},binary=['inside structure flag'])],state='Client static inside flag and fogProgress, server packet; not target status.',registry=['netherman:mansion_nether (structure)'])
path('mansion_visibility',[fog],['ENVIRONMENT'],'netherman:mansion_nether','Enter/leave a legitimately detected valid structure; ordinary fog input remains part of lerp.', ['coa3-event/MansionCheckHandler','coa3-client/ClientFogHandler','coa3-network/FogSyncS2CPacket','coa3-network/ClientPayloadHandler'])

fireids=['azazel','gilded_golem','statue_bossunit','laser','statue_entity','manipulator','guardian','ghastly']
fire=add('entity_fire_immunity','Registered entity fire immunity','BINARY_MECHANIC','Eight types are registered fireImmune: '+', '.join(fireids)+'. Native fire-tag damage rejection/ignition predicates use this type flag. This does not imply immunity to magic, lava movement, arbitrary HP writes or all other damage. Laser/Believer/Azazel state-specific hurt rejection are separate.', ['coa3-NetherExp'],'Vanilla fire-immune entity-type flag','Literal Builder.fireImmune and native Entity predicate.','New registered recipient set; no custom fire DamageType.',[component('FIRE_ELIGIBILITY','native type fireImmune boolean','VANILLA_DIRECT',binary=['eight registered types'])],registry=['netherman:'+k for k in fireids])
path('type_fire_flag',[fire],['ENVIRONMENT','OTHER'],'Eight registered fire-immune Cult types','One shared registration/predicate path; concrete eight recipient variants listed, including laser with stronger unconditional hurt override.', ['coa3-NetherExp'])
push=add('explicit_push_rejection','Explicit knockback/push rejection','BINARY_MECHANIC','Doctor, Blacksmith and StatueBossunit no-op knockback(strength,x,z) and push(x,y,z). Welcomer isPushable=false/doPush empty. Laser also no-ops knockback/push(Entity)/doPush, isPushable=false, isPickable=false and hurt=false. These overrides do not prevent direct setDeltaMovement from other mechanics; ordinary knockback-resistance attributes are separate native stats.', ['coa3-entity/DoctorEntity','coa3-entity/BlacksmithEntity','coa2-bossunit','coa2-welcomer','coa2-laser'],'Native knockback/push eligibility','Same callbacks, replaced by no-op/false.','Recipient-specific explicit overrides; not a universal motion immunity.',[component('PUSH_REJECTION','no-op named callbacks; direct velocity writes remain possible',binary=['concrete override class/method'])])
for key,wid in [('doctor','coa3-entity/DoctorEntity'),('blacksmith','coa3-entity/BlacksmithEntity'),('statue_bossunit','coa2-bossunit'),('welcomer','coa2-welcomer'),('laser','coa2-laser')]:
 path(key+'_push_guard',[push],['OTHER'],'netherman:'+key,'Concrete recipient override; retain distinct class/signature case.', [wid])
fall=add('ghastly_fall_immunity','Ghastly fall rejection','BINARY_MECHANIC','Ghastly causeFallDamage returns false and checkFallDamage is empty. Native flight/taming/nesting source context does not add a Player fall immunity.', ['coa3-entity/GhastlyEntity'],'Vanilla fall-damage eligibility','Uses native fall callbacks.','Explicit recipient override only.',[component('FALL_ELIGIBILITY','causeFallDamage=false; checkFallDamage no-op',binary=['Ghastly'])],registry=['netherman:ghastly'])
path('ghastly_fall_guard',[fall],['ENVIRONMENT'],'netherman:ghastly','Native falling callback on Ghastly; no direct damage test call required by this catalog.', ['coa3-entity/GhastlyEntity'])
repair=add('blacksmith_repair','Blacksmith paid durability repair','CUSTOM_RESOURCE','Server interaction in payment state0 consumes one Netherite Scrap unless creative and sets state2. Next damageable non-ArmorItem is copied, damage value set0, one original consumed unless creative, copy dropped toward Player and state reset0. Other components remain from copy; this repairs item durability, not HP. PaymentState saved. Anvil-seeking animation is not an eligibility requirement.', ['coa3-entity/BlacksmithEntity'],'Vanilla item durability repair','Sets native item damage value to zero.','NPC payment/state source, no anvil XP/material repair formula or enchantment removal.',[component('DURABILITY_RESET','copied stack damage=0',numbers={'damage_after':0,'payment_scrap':1},binary=['payment state2','damageable','not ArmorItem'])],state='Saved PaymentState.',registry=['netherman:blacksmith'])
path('blacksmith_paid_repair',[repair],['ACTIVE_ITEM','OTHER'],'netherman:blacksmith + Netherite Scrap + damageable non-armor item','Pay then supply eligible item through native interaction.', ['coa3-entity/BlacksmithEntity'])
potion=add('doctor_potion','Doctor parameterized native potion','VANILLA_LIKE_EXTENDED','Server golden-apple trade requires no sick Believer in AABB10. Cache all current MobEffect registry holders on first generation, choose one uniformly, build vanilla Potion with one custom MobEffectInstance duration200..1799/amplifier0..3, and drop toward Player. Native drinking instantaneous holder uses applyInstantenousEffect(drinker,drinker,drinker,amp,1); noninstant uses addEffect. Selected external holder retains its own semantics; Cult does not implement every registry effect.', ['coa3-entity/DoctorEntity'],'Vanilla Potion custom-effect components','Literal vanilla PotionItem dispatch and selected actual registry holder.','Dynamic random producer and wider parameter selection; no guarantee of a desired holder per trade.',[component('POTION_HOLDER_SELECTION','uniform actual registry holder;200+nextInt1600 ticks;nextInt4 amplifier',numbers={'min_duration':200,'max_duration':1799,'max_amplifier':3},binary=['golden apple','no sick nearby Believer']),component('NATIVE_POTION_DISPATCH','instant potency1 or noninstant addEffect','VANILLA_DIRECT',{'instant_potency':1},['holder category determines branch'])],state='Static CACHED_EFFECTS list, PotionContents component; not a new target capability.',registry=['netherman:doctor','minecraft:potion'])
path('doctor_duration_potion',[potion,get('manipulation'),get('bad_omen')]+bossrows,['ACTIVE_ITEM'],'Doctor-produced minecraft:potion','Native trade then drink a noninstant selected holder. Links are alternatives, never simultaneous payloads. Doctor may select any current holder, including previously cataloged literal holders and marker-only zones.', ['coa3-entity/DoctorEntity'])
path('doctor_instant_potion',[potion],['ACTIVE_ITEM'],'Doctor-produced minecraft:potion','Native trade selects an instantaneous holder; drink dispatches instant implementation with potency1. Do not apply duration-tick formulas to instant branch.', ['coa3-entity/DoctorEntity'])

# Corrections resolved against full installed classes, not names or old shorthand.
get('statue_observation')['custom_state']='Plain server fields isFrozen/hasAttacked, not synchronized data and not persisted by custom save overrides; default false in fresh instances.'
get('grand_door')['implementation']=proofs(['coa3-block/GrandDoorBlock','coa3-block/GrandDoorPartBlock','coa3-block/entity/GrandDoorBlockEntity','coa4-entity/GuardianEntity'])
get('grand_door')['actual_behavior']+=' Guardian checks every10 entity ticks while idle/no target/greetingCooldown0 for tamed Ghastly within15; greetingCooldown24000. Three greeting cycles use phases20/60/20 with20 intercycle pause. Only THIRD roar (phase2 timer59) scans blocks in offsets[-20,20]^3 and toggles doors with bossCooldown<=0; acquiring target aborts greeting.'
for p in P:
    if p['id'].endswith(':grand_door_guardian'):
        p['implementation']=proofs(['coa4-entity/GuardianEntity','coa3-block/entity/GrandDoorBlockEntity'])
        p['setup']='Idle targetless Guardian, greetingCooldown0, tamed Ghastly in15; native third roar scans door within20 each axis with bossCooldown<=0. Only third roar toggles, not every phase.'
get('mansion_fog')['registry_ids']=['netherman:mansion_nether']
get('doctor_potion')['actual_behavior']=get('doctor_potion')['actual_behavior'].replace('applyInstantenousEffect(drinker,drinker,drinker,amp,1)','applyInstantenousEffect(playerOrNull,playerOrNull,drinker,amp,1)')
get('azazel_wheel')['components'][0]['numerical_parameters'].pop('vertical')
get('azazel_wheel')['components'][0]['numerical_parameters']['recipient_vector_factor']=1.5
get('guardian_rapid_melee')['components'][1]['vanilla_relation']='VANILLA_DIRECT'

# Exact shared vanilla components. These are local component references, not R3
# cross-mod primitive deduplication or approval for scaling.
VANILLA={
 'invisibility':dict(formula='updateInvisibilityStatus sets invisible iff holder present. Visibility=1*(.8 if discrete else1)*(.7*max(armorCoverage,.1) if invisible else1)*(.5 for matching mob-head observer else1); armorCoverage=nonempty armor slots/armor-slot count. Installed CommonHooks.getEntityVisibilityMultiplier may modify final value. Amplifier does not change this branch.',evidence=['vanilla-evidence/cult-completion.json','vanilla-evidence/cult-final.json','reference-evidence/cult-loader-244.json','reference-evidence/cult-final-244.json']),
 'cures':dict(formula='Installed default cures MILK and PROTECTED_BY_TOTEM; POISON additionally HONEY. removeEffectsCuredBy checks instance cure membership and cancellable onEffectRemoved(cure). removeAllEffects attempts every active effect with cancellable onEffectRemoved(null), not unconditional deletion. Milk/Honey dispatch their respective cures. Raw vanilla Milk removes all; raw Honey removes Poison.',evidence=['reference-evidence/cult-final-244.json','reference-evidence/cult-loader-244.json','vanilla-evidence/cult-completion.json']),
 'death':dict(formula='Native totem checks hand item and bypasses_invulnerability veto before LivingDeathEvent, HP1, protected_by_totem cures, Regen900/1 FireResistance800/0 Absorption100/1. Cult mask/Chance use later cancellable LivingDeathEvent at HIGHEST/HIGH, no own source-tag veto, and different HP/item/location behavior. Lower normal handlers skip already canceled events by default. Native die returns before death work if onLivingDeath cancels.',evidence=['reference-evidence/vv-loader-244.json','reference-evidence/cult-final-244.json','reference-evidence/cult-loader-244.json']),
 'effect_math':dict(formula='Regeneration heals1 below max at max(1,50>>amp); Resistance uses max(0,damage*(25-5*(amp+1))/25) unless relevant bypass tags; Weakness attackDamage ADD_VALUE -4*(amp+1); Slowness movementSpeed ADD_MULTIPLIED_TOTAL -.15*(amp+1); Unluck luck ADD_VALUE -(amp+1); Absorption starts max(current,4*(amp+1)) with maxAbsorption modifier4*(amp+1). FireResistance uses native fire eligibility. Blindness full-duration fog far5, final20-tick fade; Darkness native22-tick blend toward15. Actual holder consumers remain native.',evidence=REFS),
 'collision':dict(formula='Crimson Web/Entrance/Traphive copy NETHER_WART_BLOCK (hasCollision true), not COBWEB (noCollission). ofFullCopy delegates ofLegacyCopy which copies hasCollision; noOcclusion changes only canOcclude. Inherited getCollisionShape returns state.getShape iff hasCollision. WebBlock.entityInside cobweb stuck movement is absent from these custom classes.',evidence=['native-evidence/cult-completion.json','vanilla-evidence/cult-completion.json','vanilla-evidence/cult-final.json']),
 'scheduler':dict(formula='Goal requiresUpdateEveryTick defaults false. Mob alternate full selector/every-tick-only selector means ordinary goal counters normally run every2 server ticks; entity counters every entity tick. Start/super order matters; interruption can pause/abort goals. No fixed DPS conversion.',evidence=['vanilla-evidence/cult-completion.json','reference-evidence/cult-loader-244.json']),
}
for key in ['chance_totem','mask_rescue_repair']:
    get(key)['actual_behavior']+=' Installed removeAllEffects attempts every effect but removal events can veto individual removals; see exact cure/death component comparisons.'
    get(key)['components'].append(component('EFFECT_REMOVAL','attempt each effect removal with onEffectRemoved(null); not cure-membership-limited','VANILLA_DIRECT',binary=['individual removal can be vetoed']))
    get(key)['vanilla_component_refs']=['cures','death','effect_math','invisibility']

# Audited resemblance is specific even when the operation is vanilla but its
# trigger is custom. One primary classification applies to each final package.
similarities={
 'manipulation':'Native targeting/input/rotation operations are used; no equivalent vanilla debuff.',
 'stick_pull':'Native entity velocity assignment; closest fishing pull/knockback moves targets.',
 'stick_flee':'Uses native DefaultRandomPos away search and navigation.moveTo.',
 'owned_skeleton_control':'Actual vanilla WitherSkeleton equipment/melee; custom ownership/target selection wraps it.',
 'chance_totem':'Like a vanilla totem, prevents a death, consumes an item, writes positive HP and applies literal native statuses.',
 'mask_rescue_repair':'Early-stage Regen900/1 FireResistance800/0 Absorption100/1 durations/levels match native totem; HP and item charge handling differ.',
 'mask_fire_immunity':'Rejects native fire-tag damage like FireResistance eligibility; it is an incoming-event armor predicate.',
 'crimson_arrow_ricochet':'Inherits AbstractArrow entity-hit damage and native Bow/Crossbow ammo creation.',
 'azazel_shield':'Uses native heal20 and hurt rejection; has no corresponding vanilla timed hit-count shield formula.',
 'azazel_terminal':'Uses native entity discard/loot placement; ordinary vanilla death is triggered after admitted lethal damage instead.',
 'azazel_mercy':'Uses native targeting/navigation/rotation; no vanilla mercy cinematic package.',
 'midas_fire_ring':'Actual inFire hurt request and native ignition timer.',
 'midas_inventory':'Uses native Inventory/ItemStack replacement, not a vanilla status.',
 'azazel_prison':'Native terrain collision and block replacement can confine entities.',
 'native_fangs':'Actual EvokerFangs owner/alliance/attack-timing/damage factory implementation.',
 'laser_hazard':'Actual magic damage and native fire timer, comparable to contact hazards.',
 'believer_protection':'Returns false from native hurt; no Resistance modifier calculation.',
 'believer_sickness':'Uses native navigation stop/travel input; no vanilla sickness effect.',
 'believer_healing':'Literal native LivingEntity.heal, health cap and heal event.',
 'bad_omen':'Actual BAD_OMEN holder and normal village/raid conversion retained.',
 'guardian_rapid_melee':'Actual mob_attack damage processing after an explicit vanilla hurt-cooldown field reset.',
 'guardian_mega_punch':'Native mob_attack and additive velocity; vanilla golem launch is only a comparison, not the inherited producer.',
 'welcomer_buff':'Like a damage buff changes attack outcomes; no vanilla Strength/attribute implementation.',
 'golem_healing_pull':'Native heal, magic hurt, item discard and velocity APIs; no vanilla heal-equals-damage contract.',
 'golem_launch':'Inherits actual IronGolem successful-hit launch .4*max(0,1-KR).',
}
for key in ['azazel_wind','azazel_pull','azazel_launch','azazel_wheel']:
    similarities[key]='Uses native mob_attack requests and velocity operations; these explicit vectors are not vanilla knockback formulas.'
for key,value in similarities.items():get(key)['vanilla_similarities']=value

# Explicitly separate all legitimate production chains from resulting mechanics.
SOURCE_CHAINS=[
 dict(id='cult:azazel_creation',producers=['netherman:azazel_spawn_egg','native Azazel altar event'],descendants=['netherman:azazel'],evidence=proofs(['coa3-NetherExp','coa3-event/AzazelAltarEvent']),note='Same Azazel implementation after creation; altar structure/check/consumption are acquisition prerequisites, not an extra combat effect.'),
 dict(id='cult:azazel_arrow_family',producers=['netherman:azazel state4'],descendants=['minecraft:arrow','minecraft:evoker_fangs','netherman:laser'],evidence=proofs(['coa2-azazel']),note='Variant0 ordinary ownerless arrow rain30 at targetY+10 x/z[-5,5), downward1.5; variant1 fangs20 at timers100/80/60; variant2 lasers10 radius7 at100. Preserve owner identity and concrete descendants.'),
 dict(id='cult:azazel_passive_midas',producers=['Azazel passive idle aggro 1/PASSIVE_SUMMON_CHANCE600','Midas timer110'],descendants=['netherman:statue_bossunit','netherman:statue_entity','netherman:guardian'],evidence=proofs(['coa2-azazel']),note='Passive: two Bossunits or four Statues; Midas: configured Bossunits3 or Guardians2. Their own effects/AI are cataloged under native descendant. Not new DamageTypes.'),
 dict(id='cult:manipulator_descendants',producers=['netherman:manipulator','netherman:manipulator_stick'],descendants=['minecraft:wither_skeleton','netherman:guardian','netherman:villager_prisoner','netherman:piglin_prisoner'],evidence=proofs(['coa3-entity/ManipulatorEntity','coa-stick','coa2-manipulator-convert']),note='Stick-owned skeletons carry SummonerUUID; mob skeletons do not. Manipulator successful super.hurt atHP<=10 spawns Guardian once. Conversion creates fresh prisoners. These are distinct prerequisite paths.'),
 dict(id='cult:believer_statue',producers=['Believer server die before super'],descendants=['netherman:statue_entity'],evidence=proofs(['coa2-believer']),note='Statue creation is before superclass death veto; do not assume cancellation rolls it back.'),
 dict(id='cult:nether_spawner',producers=['netherman:nether_spawner'],descendants=['netherman:'+x for x in ['manipulator','guardian','welcomer','blacksmith','doctor','gilded_golem','trader','believer']],evidence=proofs(['coa3-block/entity/NetherSpawnerBlockEntity','coa2-config']),note='Every10 world ticks when cooldown expired and nearest Player present: neighbor priority GildedBlackstone,PolishedBlackstoneBricks,PolishedBlackstoneBrickStairs,IronBlock,LapisBlock,RawGoldBlock,DiamondBlock,EmeraldBlock. Branch-specific configured cooldowns/counts; no creatorUUID for golem. Equivalent descendant class once created, except explicitly preserved owner/start-state differences.'),
 dict(id='cult:player_golem',producers=['native gold-block T plus carved pumpkin/jack-o-lantern placement'],descendants=['netherman:gilded_golem'],evidence=proofs(['coa3-event/GildedGolemSpawnEvent']),note='CreatorUUID excludes creator from healing pull/Player drain; retain separate owner-bearing path.'),
 dict(id='cult:potion_and_honey_acquisition',producers=['netherman:doctor','netherman:crimson_honey_bottle','netherman:crimson_arrow_coating recipe'],descendants=['minecraft:potion','netherman:crimson_honey_block','netherman:crimson_arrow'],evidence=proofs(['coa3-entity/DoctorEntity','coa3-item/CrimsonHoneyBottleItem','coa3-item/crafting/CrimsonArrowRecipe']),note='Doctor random holder source preserves semantic owner; bottle turns vanilla Honey to Crimson Honey; recipe coats1..5 arrows with one bottle. Native item delivery/eligibility remains.'),
]

# Per-native-mechanic compatibility attribution is deliberately conditional. These
# are reachability mappings for pinned hooks, not claims every equipped proc fires.
HOOKS={}
def hook(key,name,entries,condition,change,targets):
    ids=[k for k in W if k.startswith('coa3-compat-') and any('/'+s in W[k][1]['entry'] for s in entries)]
    assert ids,key
    HOOKS[key]=dict(id=key,name=name,attribution='GENERIC_CONDITIONAL_PRESENT',condition=condition,change=change,
        implementation=proofs(ids),effect_ids=['cultofazazel:'+t for t in targets])
native_damage=['azazel_wind','azazel_pull','azazel_launch','azazel_wheel','midas_fire_ring','native_fangs','laser_hazard','guardian_rapid_melee','guardian_mega_punch','golem_healing_pull','golem_launch','wither','poison','void_contact','pointed_blackstone_fall']
owned_damage=['azazel_wind','azazel_pull','azazel_launch','azazel_wheel','native_fangs','guardian_rapid_melee','guardian_mega_punch','golem_launch']
hook('withered_bracelet','Withered Bracelet',['WitheredBraceletItem'], 'Recipient Player, actual WITHER DamageType, equipped usable passive.', 'Cancel incoming Wither damage; does not remove the holder.', ['wither'])
hook('antidote','Antidote Vessel antidote',['AntidoteVesselItem'], 'Server Player receives nonbeneficial effect; equipped usable antidote.', 'duration=int(duration*(1-stat(antidote,amount))); includes harmful/neutral holders, not custom entity booleans.', ['manipulation','chance_totem','mask_rescue_repair','bad_omen','wither','slowness','poison','unluck','darkness','doctor_potion'])
hook('devourer','Antidote Vessel devourer',['AntidoteVesselItem'], 'Player AttackEntityEvent against LivingEntity with beneficial effects, strengthScale>.9, equipped usable devourer.', 'Remove/readd each target beneficial holder with duration reduced by stat*20, attempt transfer to attacker; native effect/remove events remain. Only beneficial bundle/selected potion branches mapped.', ['chance_totem','mask_rescue_repair','doctor_potion'])
hook('obsidian','Obsidian Skull',['ObsidianSkullItem'], 'Server Player IS_FIRE incoming; equipped usable hell with native stored-time/capacity gate.', 'Conditional cancellation; applies Midas inFire and later onFire ticks after Laser timer write, not Laser magic5 or unconditional type flag.', ['midas_fire_ring','laser_hazard'])
hook('cross','Cross Necklace',['CrossNecklaceItem'], 'Player post-damage; equipped usable invulnerability.', 'invulnerableTime+=int(stat*20); active item ticking/unequip may subtract its modifier. Guardian rapid resets before its next own request; other ordinary admitted hits retain native cooldown handling.', native_damage+['crimson_arrow_ricochet'])
hook('power','Power Glove',['PowerGloveItem'], 'Damage owner Player, equipped usable power, stored time>=5.', 'Incoming amount*=1+stat, stored time reset0. Mapped only player-owned Crimson Arrow damage path; not ownerless environmental or boss-owned damage.', ['crimson_arrow_ricochet'])
hook('vampiric','Vampiric Glove',['VampiricGloveItem'], 'Post-damage owner Player with usable equipped vampire.', 'Owner heal(min(victimMaxHP,newDamage*stat)); probability in callback is experience, not healing gate.', ['crimson_arrow_ricochet'])
hook('umbrella','Umbrella',['UmbrellaItem'], 'Player holding umbrella, using an item, no umbrella cooldown, LivingEntity source owner, normalized source-to-player look dot>=.65.', 'Cancels incoming; axe owner imposes110 cooldown. After cancellation pushes alive nonself LivingEntities inAABB3 by normalizedAway*(.4+gliderCount*.2), Y/5; Player motion uses network packet. Does not gate Cult hurt-independent movement. Ownerless magic/fire/tip fall do not enter this source-owner branch.', owned_damage+['crimson_arrow_ricochet'])
hook('kitty','Kitty Slippers',['KittySlippersItem'], 'Player reaches uncanceled death event with usable equipped rescue and native random/chance gate.', 'NORMAL death rescue HP1/cancel; Cult HIGHEST mask/HIGH Chance run first and normally prevent this lower handler from receiving the event. Competition is ordered, not simultaneous.', ['chance_totem','mask_rescue_repair'])
hook('chorus','Chorus Totem',['ChorusTotemItem'], 'Player post-damage from another LivingEntity, usable equipped past, HP>=1, missingHP*chance>=random.', 'Moves attacker, zeros velocity, tries safe spot in shrinking radius; does not rewrite source damage identity.', owned_damage+['crimson_arrow_ricochet'])
hook('thorn','Thorn Pendant',['ThornPendantItem'], 'Player post-damage from another LivingEntity, equipped usable poison and chance gate.', 'Attacker invulnerableTime0; thorns request=newDamage*multiplier then actual POISON duration=time*20 amp1 independently of retaliation hurt result.', owned_damage+['crimson_arrow_ricochet'])
hook('shock','Shock Pendant',['ShockPendantItem'], 'Server Player post-damage with nonnull owner and usable equipped lightning/chance gate.', 'Visual-only lightning entity plus explicit native lightningBolt hurt(stat damage) to owner after invulnerableTime0. Its separate Player lightning-immunity hook has no matching primary Cult lightning producer.', owned_damage+['crimson_arrow_ricochet'])
hook('cowboy','Cowboy Hat',['CowboyHatItem','mixin/LivingEntityMixin','mixin/MobMixin'], 'AI-enabled Mob with first passenger Player wearing toggled hat; native mount/ability eligibility still required.', 'Can supply controlling passenger and replace travelRidden, clear target, alter speed/input/rotation. Affects target/navigation-dependent branches only; does not remove Cult type flags or reenable no-op knockback.', ['owned_skeleton_control','stick_flee','azazel_mercy','azazel_wheel','guardian_rapid_melee','guardian_mega_punch','welcomer_buff','statue_observation','prisoner_conversion'])

# Source linkage corrections: the same holder can occur inside a larger package.
path('azazel_altar_admission',[get('azazel_shield')],['ENVIRONMENT','OTHER'],'Native Azazel altar event',
    'Altar creation explicitly initializes ATTACK_STATE10/MERCY_TICK0. Hurt is rejected and travel stopped until mercyTick>=40 returns state0. Ordinary spawn-egg construction does not initialize this cinematic; preserve the admission difference.',
    ['coa3-event/AzazelAltarEvent','coa2-azazel'])
get('azazel_shield')['actual_behavior']+=' Native altar creation starts protected state10 for40 entity ticks, unlike ordinary egg construction; separate source path preserved.'
SOURCE_CHAINS[0]['note']='Altar initializes ATTACK_STATE10/MERCY_TICK0, with native40-tick spawn admission/travel suppression; distinct from egg construction. After cinematic, same Azazel attack implementation. Structure/consumption are recorded producer prerequisites.'
HOOKS['cross']['change']=HOOKS['cross']['change'].replace('active item ticking/unequip may subtract its modifier','unequip subtracts int(modifier)')
for p in P:
    if p['id'].split(':')[1] in ['chance_hand','chance_curio','mask_death_repair']:
        p['effect_ids'].append(get('slowness')['id'])
        get('slowness')['delivery_paths'].append(p['id'])
        get('slowness')['alternate_sources'].append(p['primary_source'])
    if p['id'].endswith(':void_contact'):
        p['equivalent_sources']=['netherman:void_corner','netherman:void_mid','netherman:void_midcorner']
        for e in [get('void_contact'),get('darkness')]:
            e['alternate_sources'].extend(['netherman:void_mid','netherman:void_midcorner'])
get('slowness')['numerical_parameters'].update(chance_bundle_duration=600,chance_bundle_amplifier=0)
get('slowness')['actual_behavior']+=' Chance hand/Curios rescue and final mask rescue additionally apply600/0 as part of their own death packages; Doctor can select200..1799/0..3.'

EXCLUSIONS=[
 dict(id='zones',registry_ids=['netherman:'+k for k in ['fear','excitement','faith','anxiety']],disposition='MARKER_AUDIO_TITLE_ONLY',
      behavior='Empty ZoneEffect subclasses have no attribute, damage or control implementation. Totemus and Azazel manage actual markers; ClientZoneAmbientEvents uses them for titles/audio. Leaving Totemus radius does not itself clear; type3 removes in its own scan. Doctor can randomly produce them, but this does not create combat semantics.',evidence=proofs(['coa-zone','coa-zone-client','coa-zone-source','coa3-effect/ZoneEffect','coa3-client/ClientZoneAmbientEvents','coa3-NetherExp'])),
 dict(id='honey_bottle',registry_ids=['netherman:crimson_honey_bottle'],disposition='FOOD_AND_ACQUISITION_NOT_STATUS_CURE',
      behavior='40-tick food use nutrition6/saturationModifier.1/alwaysEdible, bottle return. Item subclass does not call HoneyBottleItem or removeEffectsCuredBy(HONEY); no native Poison cure. useOn converts vanilla Honey to Crimson Honey and coating recipe makes1..5 Crimson Arrows with one bottle. Future source alternatives link to their block/projectile records; ordinary food/saturation is not a new combat formula.',evidence=proofs(['coa4-item/CrimsonHoneyBottleItem','coa3-item/crafting/CrimsonArrowRecipe','coa3-NetherExp'])),
 dict(id='nether_void_variants',registry_ids=['netherman:voidnether_corner','netherman:voidnether_mid','netherman:voidnether_midcorner'],disposition='EMPTY_COLLISION_VISUAL_ONLY',
      behavior='Nether-suffixed blocks return empty collision and their block entities have empty controller registration; no entityInside magic/Darkness like ordinary Void variants.',evidence=proofs(['coa3-block/VoidNetherCornerBlock','coa3-block/VoidNetherMidBlock','coa3-block/VoidNetherMidCornerBlock','coa4-block/entity/VoidNetherCornerBlockEntity','coa4-block/entity/VoidNetherMidBlockEntity','coa4-block/entity/VoidNetherMidCornerBlockEntity'])),
 dict(id='ordinary_summons_arrows',disposition='SOURCE_CONTEXT',behavior='Ordinary arrows, spawn eggs, altar/NetherSpawner creation, passive/Midas summons and Believer-death Statue are preserved in source_chains. Native descendants keep their own mechanics. Normal melee/projectile damage without an additional rule is not a new special effect.',evidence=proofs(['coa2-azazel','coa3-NetherExp','coa3-block/entity/NetherSpawnerBlockEntity'])),
 dict(id='statue_stand_and_decoration',disposition='ORDINARY_GEOMETRY_RENDERING',behavior='Statue Stand and empty block entities supply geometry/rendering, not Statue entity attacks. Blackstone columns/axon/plant, trophy display and mosaic blocks are ordinary geometry/support/decor; prison actively placed terrain is separately counted.',evidence=proofs(['coa3-block/StatueStandBlock','coa4-block/entity/StatueStandBlockEntity','coa3-block/BlackstoneAxonBlock','coa3-block/BlackstonePlantBlock'])),
 dict(id='ghastly_husbandry',disposition='ACQUISITION_SOURCE_CONTEXT',behavior='Taming/nesting/pollination/honey are husbandry. Hive stores full Ghastly NBT up to5 then reloads it; not fresh prisoner replacement. No attack goal/new soul or HP drain. Tamed Ghastly is a prerequisite for the separately cataloged Guardian door path.',evidence=proofs(['coa3-entity/GhastlyEntity','coa3-entity/GhastlyBuildNestGoal','coa3-entity/GhastlyPollinateGoal','coa3-entity/GhastlyEnterHiveGoal','coa3-block/entity/GhastlyNestBlockEntity'])),
 dict(id='npc_trade_and_mining',disposition='ACQUISITION_OR_ANIMATION',behavior='Trader loot tables create ordinary items/enchants; Blacksmith raw-gold disassembly is acquisition. Blacksmith durability repair and Doctor actual effect-potion generation are separately counted. Prisoner mining animation/sounds do not destroy mining blocks. Hints, anvil-looking and note UI are not debuffs.',evidence=proofs(['coa3-entity/TraderEntity','coa3-entity/BlacksmithEntity','coa3-entity/DoctorEntity','coa3-entity/VillagerPrisonerEntity','coa3-entity/PiglinPrisonerEntity','coa4-client/ClientActionDelegate'])),
 dict(id='cosmetic_phases',disposition='VISUAL_AUDIO_ONLY',behavior='Azazel phase thresholds <=50%/<=25% drive synchronized visuals but do not scale shown attack formulas. Guardian death Weakness sound is not Weakness; Launch/death explosion particles are not damage explosions. Entity models/renderer bone rotations, emissive/hint layers, boss bars, overlays and fog color are visual; actual player input/aim and fog distance changes are separately counted.',evidence=proofs(['coa2-azazel','coa2-guardian','coa3-client/ClientEffectEvents','coa3-client/ClientFogHandler'])),
]

# Explicit local runtime fixture cover. The unit is a fixture family with its
# native descendants, not spawn-egg count, total runs, or R3 global minimization.
FIXTURE_PATHS={
 'manipulator_stick':['manipulation_melee','stick_active_pull','stick_passive_flee','stick_owned_summon','owned_skeleton_wither'],
 'chance_totem':['chance_hand','chance_curio'],
 'azazel_trophy_family':['mask_death_repair','mask_fire'],
 'crimson_arrow_with_bow_and_crossbow':['ricochet_bow','ricochet_crossbow'],
 'azazel':['azazel_shield','azazel_terminal','azazel_mercy','azazel_wind','azazel_pull','azazel_launch','azazel_wheel','azazel_midas','azazel_prison','azazel_fangs','azazel_lasers','azazel_altar_admission'],
 'believer_with_azazel':['believer_pray_protection','believer_sickness_item','believer_heal','believer_death_omen'],
 'doctor_with_believer_and_potions':['believer_sickness_doctor','doctor_push_guard','doctor_duration_potion','doctor_instant_potion'],
 'guardian_with_welcomer':['guardian_rapid','guardian_mega','welcomer_aura','welcomer_push_guard'],
 'gilded_golem_unowned_and_player_created':['golem_healing_unowned','golem_healing_creator','golem_melee'],
 'statue_bossunit':['bossunit_random_holder','statue_bossunit_push_guard'],
 'statue_entity':['statue_watch'],
 'manipulator_with_villager_piglin_ghastly':['manipulation_cast','manipulator_skeleton_wither','villager_capture_release','piglin_capture_release','ghastly_conversion_death'],
 'crimson_honey_block':['crimson_honey_landing','crimson_honey_side','crimson_honey_block_properties'],
 'eye':['eye_properties'],
 'ordinary_void_family':['void_contact'],
 'pointed_blackstone':['pointed_tip_fall'],
 'crimson_web':['crimson_web_interaction'],
 'entrance':['entrance_interaction'],
 'traphive_with_native_projectile':['traphive_contact','traphive_projectile'],
 'grand_door_with_guardian_and_tamed_ghastly':['grand_door_use','grand_door_guardian'],
 'mansion_nether_structure':['mansion_visibility'],
 'blacksmith_and_repair_items':['blacksmith_push_guard','blacksmith_paid_repair'],
 'ghastly':['ghastly_fall_guard'],
 'laser_descendant':['laser_push_guard'],
 'registered_fire_recipient_set':['type_fire_flag'],
}

def vanilla_impl(file,suffix,methods):
    obj=read_json(OUT/file)
    candidates=obj.get('classes',obj.get('witnesses',[]))
    c=next(c for c in candidates if c.get('class_name','').endswith('/'+suffix))
    assert set(methods)<={m['name'] for m in c['methods']},(suffix,methods)
    return dict(evidence_file=file,class_name=c['class_name'],methods=methods)

RAW='vanilla-evidence/cult-completion.json'
LOADER='reference-evidence/cult-loader-244.json'
VI={
 'living_damage':vanilla_impl('reference-evidence/vv-loader-244.json','LivingEntity',['hurt','actuallyHurt','canBeAffected','addEffect']),
 'living_heal':vanilla_impl(LOADER,'LivingEntity',['heal','setHealth','die','removeAllEffects']),
 'invisibility':vanilla_impl(LOADER,'LivingEntity',['updateInvisibilityStatus','getVisibilityPercent']),
 'effect_math':vanilla_impl(RAW,'MobEffect',['createModifiers','addAttributeModifiers']),
 'holder_registration':vanilla_impl(RAW,'MobEffects',['<clinit>']),
 'wither':vanilla_impl(RAW,'WitherMobEffect',['applyEffectTick','shouldApplyEffectTickThisTick']),
 'wither_skeleton':vanilla_impl(RAW,'WitherSkeleton',['doHurtTarget']),
 'poison':vanilla_impl('reference-evidence/vv-loader-244.json','PoisonMobEffect',['applyEffectTick','shouldApplyEffectTickThisTick']),
 'darkness':vanilla_impl(RAW,'FogRenderer$DarknessFogFunction',['setupFog']),
 'blindness':vanilla_impl(RAW,'FogRenderer$BlindnessFogFunction',['setupFog']),
 'regeneration':vanilla_impl(RAW,'RegenerationMobEffect',['applyEffectTick','shouldApplyEffectTickThisTick']),
 'absorption':vanilla_impl(RAW,'AbsorptionMobEffect',['onEffectStarted','applyEffectTick']),
 'bad_omen':vanilla_impl(RAW,'BadOmenMobEffect',['applyEffectTick','shouldApplyEffectTickThisTick']),
 'fangs':vanilla_impl(RAW,'EvokerFangs',['tick','dealDamageTo']),
 'iron_golem':vanilla_impl(RAW,'IronGolem',['doHurtTarget']),
 'inventory':vanilla_impl(RAW,'Inventory',['getContainerSize','getItem','setItem']),
 'arrow_item':vanilla_impl(RAW,'ArrowItem',['createArrow','asProjectile']),
 'bow':vanilla_impl(RAW,'BowItem',['releaseUsing']),
 'crossbow':vanilla_impl(RAW,'CrossbowItem',['createProjectile']),
 'arrow':vanilla_impl('reference-evidence/vv-loader-244.json','AbstractArrow',['onHitEntity']),
 'honey':vanilla_impl(RAW,'HoneyBlock',['fallOn','entityInside','isSlidingDown','doSlideMovement']),
 'slime':vanilla_impl(RAW,'SlimeBlock',['fallOn','updateEntityAfterFallOn','bounceUp']),
 'pointed':vanilla_impl(RAW,'PointedDripstoneBlock',['fallOn','spawnFallingStalactite','isStalactite','onProjectileHit']),
 'properties':vanilla_impl(RAW,'BlockBehaviour$Properties',['ofFullCopy','ofLegacyCopy']),
 'collision':vanilla_impl(RAW,'BlockBehaviour',['getCollisionShape','entityInside']),
 'potion':vanilla_impl(RAW,'PotionItem',['finishUsingItem']),
 'cures':vanilla_impl('reference-evidence/cult-final-244.json','LivingEntity',['removeEffectsCuredBy']),
 'totem':vanilla_impl('reference-evidence/vv-loader-244.json','LivingEntity',['checkTotemDeathProtection']),
 'entity':vanilla_impl(RAW,'Entity',['getBlockSpeedFactor','getBlockJumpFactor','igniteForSeconds','setRemainingFireTicks','isInvulnerableTo','causeFallDamage','push']),
 'scheduler':vanilla_impl(RAW,'Goal',['requiresUpdateEveryTick','adjustedTickDelay','reducedTickDelay']),
}
COMPARISON_MAP={
 'chance_totem':['living_heal','invisibility','effect_math','holder_registration','regeneration','blindness','cures','totem'],
 'mask_rescue_repair':['living_heal','invisibility','effect_math','holder_registration','regeneration','absorption','cures','totem'],
 'wither':['wither','wither_skeleton','living_damage'], 'poison':['poison','living_damage'],
 'slowness':['holder_registration','effect_math'],'unluck':['holder_registration','effect_math'],
 'darkness':['darkness','living_damage'],'bad_omen':['bad_omen','living_damage'],
 'native_fangs':['fangs','living_damage'],'golem_launch':['iron_golem','living_damage'],
 'golem_healing_pull':['living_heal','living_damage','entity'], 'believer_healing':['living_heal'],
 'midas_inventory':['inventory'],'crimson_arrow_ricochet':['arrow_item','bow','crossbow','arrow'],
 'crimson_honey_bounce':['honey','slime','entity'],'honey_properties':['properties','entity'],
 'pointed_blackstone_fall':['pointed','entity'], 'crimson_web_opening':['properties','collision'],
 'entrance_opening':['properties','collision'],'traphive_wave':['properties','collision'],
 'grand_door':['properties','collision','entity'],'mansion_fog':['blindness','darkness'],
 'doctor_potion':['potion','living_damage'],'entity_fire_immunity':['entity'],
 'explicit_push_rejection':['entity'],'ghastly_fall_immunity':['entity'],
 'ghastly_direct_death':['living_heal'],'guardian_rapid_melee':['living_damage','scheduler'],
 'guardian_mega_punch':['living_damage','scheduler'],'prisoner_conversion':['scheduler'],
}
METHOD_FILTER={
 'azazel_shield':['hurt','startDefenseStun','tick','travel'],
 'azazel_terminal':['hurt','startDeathCinematic','tick'],
 'azazel_mercy':['tick','startMercyPhase','mobInteract','travel'],
 'azazel_wind':['startWindAttack','performWindAttack','tick'],
 'azazel_pull':['startPullAttack','performPullAttack','tick'],
 'azazel_launch':['startLaunchAttack','performLaunchAttack','tick'],
 'azazel_wheel':['startWheelAttack','performWheelAttack','tick'],
 'midas_fire_ring':['startMidasAttack','performMidasAttack','tick'],
 'midas_inventory':['startMidasAttack','performMidasAttack','turnRandomItemToGold','tick'],
 'azazel_prison':['startPrisonAttack','performPrisonAttack','clearPrison','getHighestPrisonBlock','tick'],
 'native_fangs':['startArrowAttack','performArrowAttack','tick'],
 'believer_protection':['setProtected','hurt','tick','startPrayAttack'],
 'believer_sickness':['mobInteract','tick','travel','setSick','isSick'],
 'believer_healing':['tick'],'bad_omen':['die','tick'],
 'golem_launch':['doHurtTarget'],
}

def finalize():
    # Remove obsolete pending wording from shared historical context; the original
    # immutable note remains linked rather than being re-presented as current fact.
    for e in E:
        key=e['id'].split(':',1)[1]
        if key in METHOD_FILTER:
            for r in e['implementation']:
                selected=[m for m in r['methods'] if m in METHOD_FILTER[key]]
                if selected:r['methods']=selected
        e.pop('source_context',None)
        e['inspection_status']='VERIFIED';e['native_status']='STATIC_VERIFIED'
        e['human_summary']=e['actual_behavior']
        e['pending']=[];e['unresolved_ambiguities']=[]
        e['reference_evidence']=NATIVE+REFS
        e['vanilla_implementation']=[VI[k] for k in COMPARISON_MAP.get(key,['entity','living_damage'])]
        e['confidence']='HIGH for installed Cult native semantics and mapped conditions; static evidence, no runtime interaction or HP-loss measurement.'
        e['scalability_note']='Numerical observations only. No Stage formula, balance decision or production change.'
        e['scalable_parameters']=sorted(set(e.get('numerical_parameters',{})) | {n for c in e['components'] for n in c.get('numerical_parameters',{})})
        if key in ['ghastly_direct_death','entity_fire_immunity','explicit_push_rejection','ghastly_fall_immunity','mask_fire_immunity','blacksmith_repair']:
            e['scalable_parameters']=[]
        e['component_numerical_parameters']={str(i)+':'+c['primitive']:c.get('numerical_parameters',{}) for i,c in enumerate(e['components'])}
        e['binary_parameters']=list(dict.fromkeys(b for c in e['components'] for b in c.get('binary_parameters',[])))
        e['flags']=dict(custom_damage_source=False,custom_attributes=False,custom_state=bool(e.get('custom_state') and not e['custom_state'].startswith('No ')),
            direct_hp_write=key in ['chance_totem','mask_rescue_repair','ghastly_direct_death'],
            native_mob_effects=key in ['manipulation','chance_totem','mask_rescue_repair','bad_omen','wither','slowness','poison','unluck','darkness','doctor_potion'])
        e['damage_path'].update(source_mod_custom_damage_type=False,direct_hp_write=e['flags']['direct_hp_write'],
            shp='No Cult-defined SHP mechanism; no direct SHP subtraction in reviewed code.',
            admission='Native hurt requests retain downstream native eligibility/events/mitigation. Explicit false returns, cooldown resets, HP writes and hurt-independent side effects are stated in actual_behavior; requested damage is not observed HP loss.')
        e['hurt_return_dependency']=e['actual_behavior']
        e['duration_and_tick_semantics']=dict(behavior=e['actual_behavior'],comparison='vanilla_components.scheduler',units='Effect durations/entity counters are ticks; goal invocation counters explicitly distinguished; seconds explicitly named for ignition.')
        e['stacking']='Native MobEffect update/expiration for literal holders; custom assignments, boolean switches, per-UUID counters and item stages follow the stated callback. No invented additive stacking.'
        e['removal']='For literal effects, native expiration and installed cure/removal hooks apply; for custom state, only explicit lifecycle/reset/replacement in actual_behavior. No generic milk cure for entity/item/block state.'
        for c in e['components']:
            c['implementation']=copy.deepcopy(e['implementation'])
            c['vanilla_implementation']=copy.deepcopy(e['vanilla_implementation'])
            c['comparison_evidence']=REFS
        links=[h['id'] for h in HOOKS.values() if e['id'] in h['effect_ids']]
        e['compatibility_attribution']='GENERIC_CONDITIONAL_PRESENT' if links else 'NONE_PROVEN'
        e['existing_compat_modification']='PRESENT' if links else 'NONE'
        e['compatibility_hook_ids']=links
        e['compat_note']='Scoped to the pinned compatibility candidates/inspected matching hooks. '+('Only the listed predicate-matched hooks are attributed; other components retain Cult semantics.' if links else 'No inspected hook directly changes this native rule; no blanket full-pack absence assertion.')+' Full pack dynamic/resource precedence remains UNKNOWN outside this Cult-specific audit.'
        e['native_optional_integrations']=['Cult Curios helper for chance_curio only'] if key=='chance_totem' else []
        e['alternate_sources']=list(dict.fromkeys(e['alternate_sources']))
        assert e['primary_classification'] in CLASSIFICATIONS and e['delivery_paths']
    for p in P:
        p['status']='VERIFIED'
        p['effect_ids']=list(dict.fromkeys(p['effect_ids']))
        p['payload_selection']='Alternative one-holder selection, not all effect_ids simultaneously.' if p['id'].split(':')[-1] in ['doctor_duration_potion','bossunit_random_holder'] else 'See setup and linked per-mechanic eligibility; package components may be sequential/conditional.'
    assert {p['id'].split(':',1)[1] for p in P}=={p for v in FIXTURE_PATHS.values() for p in v}
    assert sum(map(len,FIXTURE_PATHS.values()))==len(P)

def class_coverage():
    # Single-mod closure against the already inventoried JAR; no broad scan/index
    # replacement. Archive bytes are pinned so explicit exclusions are reviewable.
    from classfile import ClassFile
    inv=read_json(OUT/'jar-inventory.json'); target=next(t for t in inv['targets'] if t['key']=='cultofazazel')
    refs={}
    for e in E:
        for p in e['implementation']:refs.setdefault(p['entry'],set()).add(e['id'])
    contexts=['NetherExp','ModSounds','config/AzazelConfig','worldgen/structure/MegaJigsawStructure','network/ModMessages','network/TotemAnimationPayload',
        'block/BlackstoneColumnBlock','block/AzazelTrophyBlock','block/MosaicChurchBlock','block/NetherSpawnerBlock','block/TotemusBlock',
        'item/GeoBlockItem','item/NoteItem','client/ClientBossBarEvents','client/ManipulationOverlay','client/ClientActionDelegate','client/ClientZoneAmbientEvents','client/sound/ZoneAmbientSoundInstance']
    covered_context={r['entry'] for ex in EXCLUSIONS for r in ex['evidence']}|{r['entry'] for chain in SOURCE_CHAINS for r in chain['evidence']}
    rows=[]
    with zipfile.ZipFile(target['path']) as jar:
        for entry in sorted(n for n in jar.namelist() if n.endswith('.class')):
            data=jar.read(entry);c=ClassFile(data);name=entry.removeprefix('com/benji/netherman/').removesuffix('.class');outer=name.split('$')[0]
            if entry in refs:disposition='MECHANIC_IMPLEMENTATION'
            elif entry in covered_context:disposition='REVIEWED_SOURCE_OR_EXCLUSION'
            elif outer.startswith(('client/model/','client/renderer/','client/layer/','client/gui/')):disposition='MODEL_RENDER_OR_UI_ONLY'
            elif outer in contexts or entry in {w['entry'] for _,w in W.values()}:disposition='REGISTRATION_SUPPORT_OR_EXCLUDED_CONTEXT'
            elif '$' in name and ('com/benji/netherman/'+outer+'.class' in refs or 'com/benji/netherman/'+outer+'.class' in covered_context):disposition='ENCLOSING_REVIEWED_CLASS_SUPPORT'
            else:raise AssertionError('Unaccounted Cult class: '+entry)
            rows.append(dict(entry=entry,sha256=byte_hash(data),superclass=c.super,disposition=disposition,effect_ids=sorted(refs.get(entry,[]))))
        resources=[dict(entry=n,sha256=byte_hash(jar.read(n)),disposition='REVIEWED_DATA_SOURCE_TAG_LOOT_RECIPE_OR_WORLDGEN') for n in sorted(jar.namelist()) if n.startswith('data/') and n.endswith('.json')]
    assert len(rows)==151 and len(resources)==62
    return dict(jar_sha256=target['sha256'],classes=rows,resources=resources,
        custom_damage_types=[],custom_attributes=[],attachments=[],mixins=[],
        note='All native classes and data resources dispositioned. Visual/support classes are not fabricated mechanics. Full broad discovery artifacts remain immutable.')

def write_review():
    finalize()
    coverage=class_coverage()
    counts=dict(sorted(Counter(e['primary_classification'] for e in E).items()))
    fixtures=[dict(id='cult_fixture:'+key,path_ids=['cultofazazel:'+p for p in paths]) for key,paths in FIXTURE_PATHS.items()]
    minimum=dict(unit='Audited fixture families; native descendants retained within setup, shared participants allowed.',
        fixture_family_count=len(fixtures),fixtures=fixtures,
        note='Local cover of all distinct path cases. Each listed family is needed for at least one named case under this setup grouping. Not a mathematical minimum number of actors/items/runs, not spawn-egg count, and not cross-mod R3 minimization.',
        shared_participants=['server Player recipient/owner plus local client for input/fog','vanilla Villager/Piglin and native descendants','Bow/Crossbow and normal projectile','Curios slot when available','native altar/spawner/player-built setup and trade/repair ingredients'],
        global_minimum_status='DEFERRED_R3')
    compat=dict(schema='tno.external_effects.cult_compat.v1',baseline=BASELINE,status='COMPLETE_WITH_SCOPED_ATTRIBUTION',
        scope='Cult-specific native rules against pinned known compatibility candidates; not full-pack runtime certification.',
        categories=['DIRECT_SOURCE_SPECIFIC','GENERIC_CONDITIONAL_PRESENT','NONE_PROVEN','UNKNOWN'],
        direct_source_specific=dict(status='NONE_PROVEN',note='No Cult-named registry override/patch found in four audited candidate source/resource sets. Absence of a name is not a generic-interaction proof.'),
        native_curios=dict(status='DIRECT_SOURCE_SPECIFIC',origin='Cult own optional integration, not an external compatibility patch',paths=['cultofazazel:chance_curio'],implementation=proofs(['coa-curios'])),
        hooks=list(HOOKS.values()),per_mechanic=[dict(effect_id=e['id'],attribution=e['compatibility_attribution'],hook_ids=e['compatibility_hook_ids']) for e in E],
        outside_scope=dict(status='UNKNOWN',detail='Runtime composition and resource precedence with every other installed mod; remaining catalog R2h/global work.'),
        candidate_jars=[dict(key=t['key'],sha256=t['sha256']) for t in read_json(OUT/'jar-inventory.json')['compat_candidates']])
    review=dict(schema='tno.external_effects.mod_review.v1',baseline=BASELINE,mod_key='cultofazazel',checkpoint=CHECKPOINT,status='COMPLETE',
        decision='CULT_OF_AZAZEL_SEMANTIC_REVIEW_COMPLETE',starting_sha=START,
        scope='Installed Cult1.1.3.1 native semantic/source/delivery review with exact raw Minecraft1.21.1 and NeoForge21.1.244 comparisons; static, no gameplay.',
        semantic_discovery_complete=True,special_damage_discovery_complete=True,source_mapping_complete=True,delivery_mapping_complete=True,
        semantic_effect_count=len(E),distinct_delivery_path_count=len(P),classification_counts=counts,
        unresolved_native_ambiguities=[],review_required_count=0,cross_mod_normalization='PENDING_R3',
        effects=E,paths=P,vanilla_components=VANILLA,source_chains=SOURCE_CHAINS,exclusions=EXCLUSIONS,coverage=coverage,
        minimum_future_sources=minimum,compatibility_attribution_file='compat-findings/cultofazazel.json',**boundary_flags())
    write_json(OUT/'compat-findings/cultofazazel.json',compat)
    write_json(OUT/'mod-reviews/cultofazazel.json',review)
    refresh(CHECKPOINT)
    accepted_reviews=[read_json(p) for p in sorted((OUT/'mod-reviews').glob('*.json'))]
    primitive_view=read_json(OUT/'behavior-primitives.json')
    primitive_view.update(checkpoint=CHECKPOINT,status='PARTIAL',
        note='Verified per-mod component instances retained within native packages, including unchanged accepted Variants components. Cross-mod deduplication/normalization and other mods remain unfinished; not R3 completion.',
        primitives=[dict(id=e['id']+':component:'+str(i),effect_id=e['id'],mod_key=e['mod_key'],status='VERIFIED_PER_MOD',**c) for r in accepted_reviews for e in r['effects'] for i,c in enumerate(e['components'])])
    write_json(OUT/'behavior-primitives.json',primitive_view)
    decision=read_json(OUT/'research-decision.json')
    decision.update(checkpoint=CHECKPOINT,status='PARTIAL',save_mode=False,save_reason=None,
        next_task='Cult COMPLETE checkpoint must be pushed and live verified. Next mod is Royal Variations2.0.4 semantic review; do not repeat Cult or Variants. Global R2 remains PARTIAL and R3/R4 are unfinished.',
        cult_decision='CULT_OF_AZAZEL_SEMANTIC_REVIEW_COMPLETE',verified_per_mod_records=len(E)+8)
    decision.pop('usage_at_save_percent',None)
    decision['checkpoints']['R2c3-partial']=START
    decision['checkpoints'][CHECKPOINT]='Self: CULT_OF_AZAZEL_SEMANTIC_REVIEW_COMPLETE; exact SHA recorded by final local/live-remote verification.'
    write_json(OUT/'research-decision.json',decision)
    lines=['# Cult of Azazel — native semantic review complete','',
        'Installed cultofazazelneo-1.1.3.1; raw Minecraft1.21.1; installed NeoForge21.1.244. Static research only.',
        '',f'{len(E)} mechanic/package records; {len(P)} distinct delivery/predicate cases; no unresolved native REVIEW_REQUIRED items.',
        '', 'Exact behavior, formulas, source chains, exclusions and references: [machine-readable review](mod-reviews/cultofazazel.json).',
        'Conditional equipment mappings: [compatibility attribution](compat-findings/cultofazazel.json).',
        '', '| Mechanic/package | Class | Primary future source | Distinct paths |', '|---|---|---|---|']
    for e in E:lines.append('| '+e['display_name']+' | '+e['primary_classification']+' | '+e['primary_test_source']+' | '+str(len(e['delivery_paths']))+' |')
    lines+=['','## Classification counts','']+[f'- {k}: {v}' for k,v in counts.items()]
    lines+=['','## Future source cover','',f'{len(fixtures)} fixture families cover all {len(P)} named cases. This is an explicit local setup cover, not a proved minimum number of actors, spawn eggs or test runs. Global minimization remains R3.']
    lines+=['']+[f'- {key}: '+', '.join(paths) for key,paths in FIXTURE_PATHS.items()]
    lines+=['','## Exclusions','']+[f"- **{ex['id']}**: {ex['behavior']}" for ex in EXCLUSIONS]
    lines+=['','## Limits and next task','','All requested native ambiguity is resolved. Known compatibility effects are conditional; full-pack runtime/resource precedence remains outside this review. No damage amount is an observed HP/SHP result. Phase 6 and production are unchanged. After commit/push/live verification, next mod is Royal Variations; R2 as a whole remains incomplete.']
    (OUT/'cult-owner-table.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps(dict(effects=len(E),paths=len(P),classifications=counts,fixture_families=len(fixtures),class_coverage=len(coverage['classes'])),indent=2))

if __name__=='__main__':write_review()
