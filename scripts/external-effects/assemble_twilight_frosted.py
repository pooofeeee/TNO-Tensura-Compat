"""Close the inspected Frosted section without promoting an unfinished mod review."""
from twilight_evidence import *
from assemble_batch import refresh
from copy import deepcopy

START='9e6775b7ea75fbfdc7e6e9f9fc0e5858d966e187'
CP='R2f2-partial'
NAME='twilightforest-r2f2-partial'


def build():
    prior=read_json(OUT/'partial-drafts/twilightforest-r2f1-partial.json')
    frost=deepcopy(prior['effects'][0])
    frost.update(display_name='Frosted status package',subsection_status='REVIEWED',classification_provisional=False,
        actual_behavior=[
         'Ordinary eligible server tick: Entity.baseTick first copies/clears powder-snow state; LivingEntity.baseTick then ticks effects; Frosted sets the flag and adds amp when amp>0/canFreeze; later LivingEntity.aiStep travel precedes native freezing (+1). With stable amp a>=0, no intervening fire/reset and canFreeze, F_next=min(140,F+a+1). Otherwise native aiStep decays by2 when not powder-snow eligible. No unconditional stun or fixed HP drain.',
         'At base Entity fire processing, remaining fire can request on_fire every20ticks and clears existing frozen ticks before effect tick. Later Entity.move can extinguish remaining fire using the Frosted powder-snow flag; its ordinary collision path is required (noPhysics/early movement branches differ). LivingEntity.baseTick extinguish check precedes Frosted application, not follows it.',
         'Movement contribution is -0.15*(a+1) ADD_MULTIPLIED_TOTAL with distinct modifier id; native frozen-ground penalty is additionally -0.05*min(F,140)/140 ADD_VALUE when standing over nonair. Native attribute order and clamping apply. These are movement penalties, not AI disabling.',
         'After gauge update and frost attribute refresh, every entity tickCount%40==0 with fully frozen/canFreeze requests ownerless minecraft:freeze amount1. Twilight incoming hook for exact minecraft:freeze replaces newDamage with originalDamage+integer(a/2). Normal nonnegative a therefore yields requested1+floor(a/2), before shield/freezing-extra/helmet/iframes/armor/magic/absorption pipeline. Expiration earlier in this tick removes the bonus while the last set powder-snow flag can still produce native gauge+1.',
         'Raw vanilla freeze tag closure: bypasses_armor, bypasses_shield, bypasses_wolf_armor, is_freezing, no_knockback, panic_causes and panic_environmental_causes. Thus native freeze bypasses ordinary armor/shield/Wolf armor, applies extra-types*5, retains Resistance/protection/absorption/cooldown, and has no native hurt knockback. Player freezeDamage=false rejects damage before incoming callback but does not itself disable the frozen gauge.',
         'For IS_FIRE incoming damage, remove Frosted, decrement the same instance amplifier, re-add if nonnegative; hidden chain and remaining duration are retained when removal succeeds. No final HP-damage gate. Fire Resistance, dead/client/invulnerable and player fireDamage/creative rejection occur before incoming event, so they prevent this hook. Shield/cooldown/armor mitigation occurs after it, so an admitted incoming event can downrank even when subsequent damage is rejected.',
         'Fresh effect amplifier clamps0..255. Normal addEffect uses loader applicability and Added events; stronger may hide old weaker state, equal amp extends longer duration, weaker longer duration can be hidden. There is no additive amp stacking. Every tick applies before duration decrement; hidden durations also decrement and may be restored. Removal/expiration are event-vetoable; server attribute removal/refresh follows successful native lifecycle.',
         'Default NeoForge cures for fresh Frosted are milk and protected_by_totem; honey is only added for Poison and does not cure Frosted. Removal does not directly zero frozenTicks; ordinary decay follows unless some other flag/gauge producer remains. Fire remove/readd ignores removal return: an external removal veto can leave the same live instance mutated and normal attribute refresh need not occur; this is retained native hook behavior, not a proposed fix.',
         'Helper excludes freeze-immune entity types, any freeze-immune wearable in HEAD/CHEST/LEGS/FEET, and creative Players. Native LivingEntity.canFreeze additionally excludes spectators and BODY freeze-immune wearables. Those extra exclusions block buildup/periodic freeze, not necessarily the status movement modifier. Environment enforcement uses direct addEffect and deliberately does not repeat helper equipment checks.',
        ],
        vanilla_similarities=['Slowness coefficient and native attribute lifecycle; native gauge140 threshold, ground penalty and40tick freeze cadence; standard effect merge/expiration and default loader cures.'],
        vanilla_differences=['Additional powder-snow flag/gauge producer, exact-freeze amount adjustment and incoming-fire downrank; source-specific helper restrictions; different native delivery prerequisites below.'],
        components=[
         dict(primitive='MOVEMENT_ATTRIBUTE',formula='-0.15*(amp+1) ADD_MULTIPLIED_TOTAL',vanilla_relation='Same Slowness coefficient, distinct modifier id',numerical_parameters={'coefficient':-.15},binary_parameters=['attribute availability','native clamp']),
         dict(primitive='POWDER_SNOW_AND_FROZEN_GAUGE',formula='stable eligible server tick min(140,F+amp+1); ordinary inactive decay max(0,F-2)',vanilla_relation='Custom status drives native environment/gauge processing',numerical_parameters={'threshold':140,'native_increment':1,'decay':2},binary_parameters=['canFreeze','server/alive','no intervening reset']),
         dict(primitive='NATIVE_FREEZE_DAMAGE',formula='tickCount%40==0 and F>=140/canFreeze: ownerless minecraft:freeze request1; incoming exact-type bonus floor(amp/2)',vanilla_relation='Native freeze source; custom incoming bonus',numerical_parameters={'interval':40,'base_request':1},binary_parameters=['exact type','active effect at incoming event','normal admission']),
         dict(primitive='FIRE_DOWNRANK',formula='remove; sameInstance.amp--; re-add if amp>=0',vanilla_relation='Custom state transition through native effect events',numerical_parameters={'amplifier_change':-1},binary_parameters=['incoming IS_FIRE','not canceled','pre-event immunity admission']),
        ],
        implementation=native_refs('init/TFMobEffects','potions/FrostedEffect','enchantment/ApplyFrostedEffect','events/EntityEvents'),
        existing_compat_modification='GENERIC_CONDITIONAL_PRESENT',compat_note='Antidote can shorten harmful Frosted duration on a qualifying equipped ServerPlayer. See scoped compat mapping; no direct Twilight patch proven in four candidates.',
        pending=['Full Twilight semantic discovery, final package/delivery deduplication and final promotion remain unfinished. Frosted local semantics and the seven original producer contracts are closed.'],
        unresolved_ambiguities=None)
    paths=[]
    def path(id,labels,source,behavior,*classes,effects=None,alternates=None,controls=None):
        paths.append(dict(id='twilightforest:'+id,mod_key='twilightforest',status='DRAFT',subsection_status='REVIEWED',
            effect_ids=effects or [frost['id']],labels=labels,primary_source=source,alternate_sources=alternates or [],
            setup=behavior,actual_native_contract=behavior,fixture_controls=controls or [],implementation=native_refs(*classes)))
    helper='Helper entity/equipment/creative eligibility and native addEffect admission apply.'
    path('frosted:ice_sword',['MELEE','ACTIVE_ITEM'],'twilightforest:ice_sword used by Player',
         'Server Player.attack requires target.hurt true before ItemStack.hurtEnemy; multipart parent is resolved for the item callback. SwordItem.hurtEnemy returns true, so Ice Sword then helper200/2. Native sweep secondary victims do not receive the item hurtEnemy callback. '+helper,
         'item/IceSwordItem','enchantment/ApplyFrostedEffect','init/TFItems',controls=['successful primary hit','rejected primary hurt','secondary sweep victim','freeze immune / leather / creative recipient'])
    for ammo,payload in [('ordinary','No retained extra parent effect.'),('tipped','Parent Arrow adds base potion effects with max(duration/8,1), plus custom effects with their stored durations.'),('spectral','Parent SpectralArrow adds Glowing for its native stored duration (default200).')]:
        path('frosted:ice_arrow_'+ammo,['PROJECTILE','ACTIVE_ITEM'],'twilightforest:ice_bow with '+ammo+' arrow',
             'Installed ProjectileWeaponItem.createProjectile creates parent, sets its critical flag, then calls customArrow. IceBow constructs IceArrow and retains parent only in memory. Constructor recreates weapon/piercing/spawn effects but does not copy parent critical flag (normal full-charge critical bonus is lost). Native impact cancellation/target deflection can prevent onHitEntity altogether. Once entered, IceArrow calls super then helper200/2 on server LivingEntity independent of hurt success, including early return/discard inside super. Parent doPostHurtEffects requires successful inherited hurt and non-Enderman living post-hit branch. '+payload+' On reload parentArrow=null; retained potion/spectral callback is lost, Frosted remains. '+helper,
             'item/IceBowItem','entity/projectile/IceArrow','entity/projectile/TFArrow','enchantment/ApplyFrostedEffect',
             controls=['normal hit','hurt false/shield/cooldown','impact event canceled or parried','native target deflection','full draw critical flag','save/load before impact'])
    path('frosted:yeti_armor_retaliation',['ARMOR_PROC'],'Victim wearing one or more YetiArmorItem pieces; Living causing attacker',
         'EntityEvents @Component setup is invoked by BeanContext PostConstruct processor and registers LivingDamageEvent.Post. Count armor-slot YetiArmorItem instances n; originalDamage>0 and Living source owner are required. helper(5*n+5,n,n>0). Post is emitted by native actuallyHurt even with zero final HP damage after reductions; a rejection before actuallyHurt produces no Post. Retaliation targets causing owner rather than projectile. '+helper,
         'events/EntityEvents','item/YetiArmorItem','init/TFItems','enchantment/ApplyFrostedEffect',controls=['n1..4','absorption/zero final damage','early incoming cancellation','projectile with Living owner','ownerless source'])
    path('frosted:chill_aura',['ARMOR_PROC','MELEE','PROJECTILE'],'Native twilightforest:chill_aura armor enchantment on attack victim',
         'Installed enchantment JSON configures POST_ATTACK, enchanted=victim, affected=attacker. Native EnchantmentHelper equipment iteration tests slot match and per-item enchantments. For each qualifying item levelL (normal1..3), chance0.15*L invokes sequential AllOf: helper200/max(0,L-1), then enchanted-item durability request2 even if helper rejects recipient. Target is causing attacker, not projectile. Player primary melee, native mob melee and admitted arrow post-attack callbacks are legitimate producers; this is not a generic LivingDamageEvent subscription. Player sweep secondary post-attack callback is not gated by that secondary hurt return. Native normal primary/arrow return gates still apply. '+helper,
         'init/TFEnchantmentEffects','enchantment/ApplyFrostedEffect',
         alternates=['Native enchanted book from aurora_room loot; normal armor slot item with Chill Aura','melee versus owner-attributed arrow post-attack callbacks'],
         controls=['levels1/2/3 probability and amp','multiple qualifying pieces','rejected helper still requests2 durability','primary rejected hit','secondary sweep hurt false','projectile causing owner versus direct entity'])
    path('frosted:frost_enforcement',['ENVIRONMENT'],'snowy_forest without progress_lich; glacier without progress_yeti',
         'Registered PlayerTickEvent.Post checks ServerPlayer/server, tickCount%20==0, tfEnforcedProgression gamerule (defaulttrue), not creative/spectator. Biome restriction must exist and required advancement not complete. Native PlayerHelper implementation checks first advancement; both frost records have exactly one. Every60ticks and normal tick rate: snowy_forest direct addEffect100/0, glacier100/1. No helper armor/type filter: freeze-immune gear can prevent gauge while retaining status movement modifier. No world gamerule was changed/read as an active runtime fixture.',
         'events/ProgressionEvents','util/Restriction','util/Enforcement','init/custom/Enforcements','util/PlayerHelper','util/landmarks/LandmarkUtil','init/TFGameRules',
         controls=['both biomes','required advancement complete','gamerulefalse','creative/spectator','freeze-immune wearables'])
    bombid='twilightforest:ice_bomb_package'
    for producer,source,launch in [
      ('player','twilightforest:ice_bomb used by Player','Consumes1 item on server; shooter owner; speed1.25, inaccuracy1, pitch offset-5.'),
      ('dispenser','Dispenser containing twilightforest:ice_bomb','RegistrationEvents common setup invokes TFDispenserBehaviors.init -> registerProjectileBehavior. IceBombItem.asProjectile creates ownerless bomb; native default dispenser speed1.1/inaccuracy6 and consumes1 item.'),
      ('alpha_yeti','Alpha Yeti ranged attack','Registered RangedAttackGoal reaches performRangedAttack only if !canRampage; living boss owner; speed1.6, inaccuracy14-4*difficultyId, vertical aim adds horizontalDistance*.2.')]:
        for mode in ['contact','zone']:
            details=('Native projectile contact with LivingEntity: m=2; does not discard, set hasHit or start zone timer. Continued native collision processing can cause further contact callbacks; no extra bomb contact cooldown.' if mode=='contact' else
                     'Block hit sets hasHit/zero motion; timer starts101 and decrements each tick. Area callbacks occur at100/80/60/40/20/0, final callback before discard. AABB inflated(3,2,3), owner excluded; m=1. Yeti branch replaces two positions with ice and discards the Yeti before damage eligibility; it is not health damage. Terrain pass radius2 at block hit and3 when timer99 freezes water, changes default lava to obsidian, and manipulates snow/tagged vegetation.')
            path('ice_bomb:'+producer+'_'+mode,['THROWN_PROJECTILE'] if mode=='contact' else ['AOE','ENVIRONMENT'],source,
                 launch+' '+details+' Non-freeze-immune type requests twilightforest:frozen for m*(5 if freeze-hurts-extra type else1); then helper(100*m,0) regardless of hurt return. Source direct=bomb, causing=current owner. Armor/wearable helper rejection does not suppress the damage request. On save/load, bomb overrides omit parent save/load, so owner is lost and original thrower no longer receives zone owner exclusion. '+helper,
                 'entity/projectile/IceBomb','item/IceBombItem','dispenser/TFDispenserBehaviors','events/RegistrationEvents','entity/boss/AlphaYeti','enchantment/ApplyFrostedEffect','init/TFDamageTypes',
                 effects=[frost['id'],bombid],controls=['heat-sensitive type','freeze-immune type','freeze-immune wearable','hurt false','owner/nonowner','Yeti in landed zone','save/load owner loss'])
    frost['delivery_paths']=[p['id'] for p in paths]
    frost['primary_test_source']=paths[0]['primary_source']
    frost['alternate_sources']=[p['primary_source'] for p in paths[1:]]
    bomb=dict(id=bombid,mod_key='twilightforest',display_name='Ice Bomb attack and lingering freeze zone',inspection_status='DRAFT',subsection_status='REVIEWED',
        primary_classification='CUSTOM_DAMAGE',classification_provisional=False,registry_ids=['twilightforest:frozen','twilightforest:ice_bomb'],
        actual_behavior='Custom frozen damage request plus helper Frosted, repeat landed AoE, owner exclusion, terrain changes and special Yeti replacement. Damage and status have independent admission; see source variants and shared damage profile.',
        closest_vanilla_equivalent='Thrown projectile collision + native hurt pipeline, powder-snow/freezing status primitives; no vanilla attack with this complete zone/Yeti replacement package.',
        vanilla_similarities=['Native projectile impact admission, owner handling, hurt/armor/shield/resistance/enchantment/absorption/cooldown and effect processing.'],
        vanilla_differences=['Custom DamageType, explicit heat-sensitive multiplier, persistent zone, hurt-independent Frosted, terrain mutations and Yeti discard.'],
        components=[dict(primitive='CUSTOM_DAMAGE_REQUEST',formula='m*(heatSensitive?5:1), m=2 contact /1 zone',vanilla_relation='Custom frozen DamageType through native hurt'),
                    dict(primitive='FROSTED',formula='duration100*m, amp0; helper independent of hurt result',vanilla_relation='References Frosted package; not a duplicate standalone status'),
                    dict(primitive='REPEATED_ZONE',formula='timer101 -> callbacks100,80,60,40,20,0; AABB inflate3,2,3',vanilla_relation='Custom entity timer and victim query'),
                    dict(primitive='YETI_REPLACEMENT',formula='zone Yeti -> ice at old position and above; discard entity',vanilla_relation='Binary world/entity replacement, not HP subtraction'),
                    dict(primitive='TERRAIN_FREEZE',formula='initial range2; timer99 range3; native block rules in doTerrainEffects/doTerrainEffect',vanilla_relation='Custom environmental changes')],
        numerical_parameters={'contact_multiplier':2,'zone_multiplier':1,'heat_sensitive_multiplier':5,'zone_initial_timer':101,'zone_interval':20,'zone_inflate':[3,2,3]},
        scalable_parameter_candidates=['damage request','status duration','zone interval','zone lifetime','zone bounds'],
        binary_parameters=['native projectile impact','freeze-immune type','owner exclusion in zone','Yeti replacement','world block identities'],
        delivery_paths=[p['id'] for p in paths if bombid in p['effect_ids']],primary_test_source='Player ice_bomb contact and landed zone',
        alternate_sources=['Ownerless dispenser','Alpha Yeti ranged throw','Saved/reloaded bomb loses owner'],
        implementation=native_refs('entity/projectile/IceBomb','item/IceBombItem','init/TFDamageTypes','entity/projectile/TFThrowable'),
        existing_compat_modification='GENERIC_CONDITIONAL_PRESENT',compat_note='Player recipient/owner hooks are conditional; ownerless and boss-owned branches differ. No global pack guarantee.',
        pending=['Full Twilight semantic discovery and final promotion; Alpha Yeti other attacks and defenses remain a separate unreviewed section.'],unresolved_ambiguities=None)
    damage_profile=dict(type='twilightforest:frozen',status='USED',callers=[dict(entry='twilightforest/entity/projectile/IceBomb.class',method='inflictDamage')],
        direct_entity='IceBomb',causing_entity='current owner; null for dispenser and reloaded bomb',amount='m*(freeze_hurts_extra_types?5:1)',
        relevant_tags=['minecraft:bypasses_wolf_armor','neoforge:is_magic'],
        not_tagged=['minecraft:is_freezing','minecraft:is_projectile','minecraft:is_fire','minecraft:is_explosion','minecraft:bypasses_armor','minecraft:bypasses_shield','minecraft:bypasses_enchantments','minecraft:bypasses_resistance','minecraft:bypasses_invulnerability','minecraft:bypasses_cooldown','minecraft:no_knockback','minecraft:damages_helmet'],
        identity_note='Freezing DamageEffects value is a hurt effect, not IS_FREEZING membership. No automatic native freezing*5 and no Frosted exact-minecraft:freeze bonus; explicit multiplier is applied once.',
        mitigation='Normal armor/toughness, facing shield using bomb source position, Resistance, protection enchantments, absorption and hurt cooldown apply; Wolf body-armor special absorption is bypassed. No percentage damage, direct HP write, cap or floor in bomb method.',
        difficulty='WHEN_CAUSED_BY_LIVING_NON_PLAYER: Player victim scales AlphaYeti-owned request to0 Peaceful, min(amount/2+1,amount) Easy, unchanged Normal, amount*1.5 Hard before LivingEntity incoming hook. Player-owned and ownerless requests are not difficulty-scaled by this policy.',
        damage_vs_status='Damage result is ignored for subsequent helper. Yeti zone replacement bypasses this method entirely and uses discard rather than damage.',
        tag_scope='Pinned Twilight contributions plus raw Minecraft1.21.1/installed NeoForge tags; arbitrary other pack/datapack mutations are not inferred.')
    compat=deepcopy(read_json(OUT/'compat-findings/royalvariations.json'))
    candidate_rows=[]
    for t in read_json(OUT/'jar-inventory.json')['compat_candidates']:
        hits=[];inputs=[]
        for name in ['class-index.json','resources.json']:
            p=WORK/t['key']/name
            assert p.exists(),p
            data=read_json(p);inputs.append(dict(path=str(p),sha256=sha256(p)))
            rows=data if isinstance(data,list) else [dict(entry=k,value=v) for k,v in data.items()]
            hits.extend(r.get('entry',r.get('name')) for r in rows if any(s in json.dumps(r).lower() for s in ['twilightforest','frosted']))
        candidate_rows.append(dict(key=t['key'],jar_sha256=t['sha256'],twilight_name_hits=hits,reused_index_inputs=inputs))
    hooks=[]
    for h in compat['hooks']:
        if h['id']=='devourer':continue
        hooks.append(dict(id=h['id'],implementation=h['implementation']))
    compat_out=dict(schema='tno.external_effects.twilight_compat.v1',baseline=BASELINE,status='REVIEWED_FROSTED_SUBSET',candidate_jars=candidate_rows,
        direct_source_specific='NONE_PROVEN',generic_attribution='GENERIC_CONDITIONAL_PRESENT',hooks=hooks,
        matches=dict(antidote='Nonbeneficial Frosted on equipped ServerPlayer: duration=int(duration*(1-stat)).',
                     power='Player-owned Ice Arrow/Bomb incoming damage can multiply by1+stat after stored time>=5; excludes ownerless/boss owner.',
                     vampiric='Player-owned post-damage can heal owner min(victimMaxHP,newDamage*stat).',
                     cross='Qualifying Player post-damage can extend invulnerableTime by int(stat*20).',
                     umbrella='Qualifying blocking/using Player facing Living owner can cancel incoming; Frosted hurt-independent callbacks can still run if projectile impact was already admitted.',
                     kitty='Qualifying Player death rescue remains generic native death-event competition.',
                     chorus='Qualifying Player post-damage with another Living owner can relocate attacker.',
                     thorn='Qualifying Player post-damage may retaliate with thorns plus Poison.',
                     shock='Qualifying Player post-damage with owner may retaliate using lightning damage.'),
        negative_matches=['Beneficial-effect Devourer transfer does not match harmful Frosted.','No custom type is rewritten merely because the source name says frozen.'],
        scope='Four pinned candidates only, reusing prior native hook evidence. No direct Twilight-specific patch found in their indexed classes/resources. Other installed mods and dynamic composition are outside this scoped attribution; no fixes.')
    write_json(OUT/'compat-findings/twilightforest-frosted.json',compat_out)
    reference_files=['vanilla-evidence/twilight-frosted.json','reference-evidence/twilight-frosted-244.json','vanilla-evidence/variants-prerequisites.json','vanilla-evidence/vv-completion.json','reference-evidence/vv-loader-244.json','vanilla-evidence/cult-completion.json','reference-evidence/cult-loader-244.json','reference-evidence/cult-final-244.json','vanilla-evidence/royalvariations.json','reference-evidence/royal-loader-244.json','vanilla-evidence/royal-final.json']
    section=dict(schema='tno.external_effects.semantic_section.v1',baseline=BASELINE,mod_key='twilightforest',checkpoint=CP,
        status='REVIEWED_SUBSET_NOT_MOD_COMPLETE',starting_sha=START,semantic_coverage_complete=False,promoted_to_catalog=False,
        closed_areas=['Frosted native/vanilla/loader lifecycle comparison','All seven R2f1 producer contracts; configured Chill Aura proven','Ice Bomb contact/zone and ownership variants','Scoped compatibility attribution for this subset'],
        effects=[frost,bomb],paths=paths,damage_profiles=[damage_profile],
        original_seven_path_closure={p['id']:'Resolved in current source cases; no codec-only assumption retained.' for p in prior['paths']},
        comparison_evidence=[dict(evidence_file=f,sha256=sha256(OUT/f)) for f in reference_files],
        source_registration_evidence=native_refs('TwilightForestMod','beanification/BeanContext','beanification/processors/finalize/PostConstructAnnotationFinalizeBeanProcessor','beanification/processors/gather/ComponentAnnotationGatherBeanProcessor','beanification/processors/construct/ConstructBeanProcessor','events/EntityEvents','events/ProgressionEvents','events/RegistrationEvents','init/TFEnchantmentEffects','init/TFItems','init/TFEntities'),
        compatibility_file='compat-findings/twilightforest-frosted.json',
        exclusions=['Effect color/icon; arrow/sword/bomb particles and sounds are presentation, not additional damage.','IceBow repair ingredient and enchantment loot acquisition are not separate combat mechanics.','Bean registration and worldgen/advancement hints are infrastructure; actual progression-applied status remains included.'],
        future_source_cover=['Player Ice Sword primary hit','Ice Bow ordinary/tipped/spectral ammo, failed hurt and save/load controls','Player Ice Bomb contact and zone','Ownerless dispenser Ice Bomb','Alpha Yeti ranged Ice Bomb','Yeti armor retaliation','Chill Aura enchanted victim with native melee/arrow/secondary sweep callbacks','Snowy Forest and Glacier native progression enforcement'],
        source_cover_note='Subset producer cover only, not global R3 minimum runs. No boss spawn/runtime was executed.',
        exact_next_task='Begin systematic boss section with Naga and Lich, especially actual breaks_lich_shields admission. Other bosses, mobs, items, 39 remaining DamageType caller dispositions and final mod closure remain unfinished.',
        **boundary_flags())
    write_json(OUT/'semantic-sections/twilightforest-frosted.json',section)
    draft=dict(schema='tno.external_effects.partial_draft.v1',baseline=BASELINE,mod_key='twilightforest',status='PARTIAL',checkpoint=CP,
        starting_sha=START,semantic_coverage_complete=False,promoted_to_catalog=False,effects=section['effects'],paths=paths)
    write_json(OUT/'partial-drafts'/f'{NAME}.json',draft)
    review=read_json(OUT/'mod-reviews/twilightforest.json')
    review.update(checkpoint=CP,scope='R2f2 PARTIAL: Frosted/producer section reviewed, two package drafts and13 delivery cases; all boss and remaining mod closure pending. Zero final records promoted.',
        draft_file=f'partial-drafts/{NAME}.json',notes_file='semantic-sections/twilightforest-frosted.json',draft_mechanic_count=2,draft_path_count=len(paths),exact_next_task=section['exact_next_task'])
    write_json(OUT/'mod-reviews/twilightforest.json',review)
    refresh(CP)
    for f in ['effect-catalog.json','effect-sources.json','delivery-path-matrix.json','vanilla-comparison.json','behavior-primitives.json']:
        d=read_json(OUT/f);d.update(checkpoint=CP,unfinished_review=dict(mod_key='twilightforest',status='PARTIAL',draft_file=review['draft_file'],promoted_records=0));write_json(OUT/f,d)
    decision=read_json(OUT/'research-decision.json')
    decision.update(checkpoint=CP,save_mode=False,save_reason=None,next_task=section['exact_next_task'],
        recovery_twilightforest_resume=dict(local_start=START,live_remote_start=START,working_tree_start='CLEAN',divergence='0/0',newer_work=False,restarted_research=False))
    decision['checkpoints'].update({'R2f1-partial':START,CP:'Self: Frosted subsection checkpoint; exact SHA reported after live verification.'})
    write_json(OUT/'research-decision.json',decision)
    (OUT/'twilightforest-owner-table.md').write_text('''# Twilight Forest — R2f2 partial, Frosted section reviewed

The installed4.8.3345 review is **PARTIAL**. Frosted and its seven original producer contracts are now resolved, with two reviewed package drafts and13 source/path cases. **Zero final Twilight records are promoted.** Full mod mechanic, boss, defense, item and final source totals remain unknown. The four accepted reviews remain116 mechanics/161 paths/217 components. No runtime tests were performed.

| Mechanic | Native behavior | Vanilla comparison | Classification / source coverage |
|---|---|---|---|
| Frosted | Stable eligible server tick adds amp+1 to frozen gauge, capped140. Movement modifier -0.15*(amp+1) total multiplier, plus native ground frost penalty. Native freeze request every40ticks when fully frozen; exact-freeze incoming bonus floor(amp/2). Admitted incoming fire down-ranks amplifier. | Shares Slowness coefficient and native freeze processing; additional state and incoming hooks make the complete status custom. Native add/merge/expire/cures remain. | CUSTOM_STATUS; Ice Sword, three Ice Bow ammo cases, armor, Chill Aura, two biome settings, all six bomb source/mode cases |
| Ice Bomb package | Contact request2 or10; zone request1 or5, using custom frozen type. Frosted follows independently of hurt return. Landed zone runs six20tick callbacks in inflated AABB3/2/3. Yeti zone branch becomes ice blocks and is discarded. | Custom request/zone/control package through native damage and effect processing. Not vanilla freeze damage or direct HP subtraction. | CUSTOM_DAMAGE; player/dispenser/Alpha Yeti, each contact and zone |

| Source | Exact important distinction | Future fixture |
|---|---|---|
| Ice Sword | Player primary hurt must succeed before item callback200/2. Sweep secondary victims do not get the item callback. | Primary success/failure and secondary sweep controls |
| Ice Bow, ordinary/tipped/spectral | Once onHitEntity is entered, Frosted200/2 is independent of hurt result. Impact cancellation/deflection can prevent entry. Parent potion/glowing callback needs successful inherited hurt. Parent critical flag is not copied. Parent callback is lost after reload. | Three ammo paths; failed hurt; parry/deflection; full draw; save/load |
| Yeti armor | LivingDamageEvent.Post, originalDamage>0, n pieces: causing Living attacker receives5n+5ticks/amp n. Post can exist with zero final HP damage. | Piece counts, absorption, early cancellation, projectile owner versus ownerless |
| Chill Aura | Actual installed enchantment: per matching item chance0.15*level,200ticks/amp(level-1), then item durability request2 even if Frosted helper rejects. Targets causing attacker. | Native melee/arrow post-attack and secondary sweep controls, levels1–3 |
| Biome enforcement | Every60ticks: Snowy Forest100/0 without progress_lich, Glacier100/1 without progress_yeti; progression gamerule required, noncreative/nonspectator. Does not use helper equipment filter. | Both biomes, advancement/gamerule and freeze-immune gear controls |
| Player Ice Bomb | Owner=Player; speed1.25/inaccuracy1/pitch-5. Contact and zone differ. | Owned contact + zone, owner exclusion |
| Dispenser Ice Bomb | Proven native registration; ownerless, speed1.1/inaccuracy6. | Ownerless contact + zone |
| Alpha Yeti Ice Bomb | Native ranged goal, !canRampage; speed1.6, inaccuracy14-4*difficultyId. Living boss owner enables native difficulty scaling for Player victims. | Boss-owned contact + zone; only future testing |

Frosted's helper rejects freeze-immune entity types, freeze-immune head/chest/legs/feet wearables and creative Players. Native canFreeze also checks spectator and BODY armor, so some recipients can receive movement slowdown without building freeze. Fresh Frosted uses default milk/totem cures; honey does not cure it. Fire Resistance and other pre-incoming immunity gates prevent the fire down-rank callback. Later shield/cooldown rejection does not necessarily prevent it.

Ice Bomb's `twilightforest:frozen` is tagged magic and bypasses wolf armor, **not ordinary armor**. It lacks IS_FREEZING, projectile, fire, explosion, normal armor/shield/enchantment/Resistance/iframe bypass and no-knockback tags in the scoped native sources. Its explicit heat-sensitive multiplier occurs once. Normal mitigation applies. Save/load omits parent projectile serialization, losing owner and therefore original-thrower zone exclusion. Requests are not measured HP loss.

One registered custom MobEffect: `twilightforest:frosted`. Forty custom damage declarations remain pinned from R2f1; **frozen now has a reviewed caller profile**, while39 caller dispositions remain unfinished. They are not classified as unused. REVIEW_REQUIRED0; unfinished review is not ambiguity. Final VANILLA_DIRECT/COMPOSITE/EXTENDED lists are not available yet. No boss or boss-defense review is closed.

Four pinned compatibility candidates have no direct Twilight name hits; generic conditional hooks remain, including Antidote duration reduction and player recipient/owner damage hooks. This is scoped static attribution, not pack-wide compatibility. No production fixes were made.

Particles, sounds, color/icon, repair/acquisition and registration infrastructure are excluded as separate combat mechanics. Other mod areas remain unreviewed. Subset fixtures are preserved; global minimum runtime runs remain R3.

Details: [reviewed section](semantic-sections/twilightforest-frosted.json), [current drafts](partial-drafts/twilightforest-r2f2-partial.json), [compat mapping](compat-findings/twilightforest-frosted.json), [progress validation](twilightforest-progress-integrity.json), [full validation](r2f2-partial-validation.json).

Next: Naga and Lich systematic boss review, especially actual Lich shield-source admission. All remaining bosses, mobs, items, damage callers and final promotion remain pending. Ice and Fire is UNSTARTED. Phase6/production/Stage remain unchanged. R2f1 evidence remains preserved rather than redone.
''',encoding='utf-8')
    print(json.dumps(dict(checkpoint=CP,reviewed_packages=2,path_cases=len(paths),promoted=0)))


if __name__=='__main__':build()
