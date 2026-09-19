"""Assemble the bounded Friends & Foes review after native discovery/comparison."""
from review_friends import *
import subprocess

EXCLUSIONS=[
 dict(id='registered_reach_utility',behavior='Exactly one registered custom MobEffect: friendsandfoes:reach, BENEFICIAL. BLOCK_INTERACTION_RANGE ADD_VALUE=config modifier1*(amplifier+1), not ENTITY_INTERACTION_RANGE/attack reach; tick predicatefalse. Native Reaching potions duration config3600*20=72000/0, long144000/0, strong(3600//2)*20=36000/1. Standard effect merge/modifier/cure applies. Utility excluded from combat count, not silently missing.',evidence=proof('common/init/FriendsAndFoesStatusEffects',EN+'effect/ReachStatusEffect','common/init/FriendsAndFoesPotions')),
 dict(id='ordinary_gear',behavior='Wildfire Crown is ordinary ArmorItem helmet: defense3/toughness1/knockback resistance0, durability37*11=407, item fire-resistant. Only its conditional Fire Resistance proc counted. Crab claw/fragments have no combat item callback; spawn eggs and block items acquisition only.',evidence=proof('common/init/FriendsAndFoesItems','common/init/FriendsAndFoesArmorMaterials')),
 dict(id='moobloom_acquisition',behavior='Moobloom variants/flower feeding, bowl milking and shearing are acquisition/transformation of farm resources, not an attack/status cast. Bowl copies native SuspiciousStewEffects from the variant flower or EMPTY; vanilla SuspiciousStewItem owns consumption. Buttercup is FlowerBlock(SATURATION,6f); no bespoke Saturation implementation. Shearing copies health/body/name/persistence/invulnerable to ordinary Cow, then discards Moobloom; no combat transformation trigger. Bee pollination adds ordinary farming behavior; hurt cancels custom pollination before parent hurt but changes no amount.',evidence=proof(EN+'MoobloomEntity','common/init/FriendsAndFoesBlocks',MX+'BeeEntityMixin',EN+'ai/goal/bee/BeePollinateMoobloomGoal')),
 dict(id='glare_dormant_hand_heal',behavior='tryToHealWithGlowBerries is real code but cannot be reached with installed glare_tempt_items: caller requires glow berries AND !isFood, while food/tempt predicate includes glow berries. Do not use it as a positive runtime source without independently justified tag changes. Native dropped-berry pickup and periodic healing are counted.',evidence=proof(GL,'data/friendsandfoes/tags/item/glare_tempt_items.json')),
 dict(id='ordinary_crab',behavior='Crab native retaliatory melee/base stats, climbing/navigation, dancing, egg placing and claw acquisition have no distinct harmful status/projectile. Its native arthropod/underwater-breath tags are retained in defenses; no Reach buff is applied by a crab attack.',evidence=proof(EN+'CrabEntity')),
 dict(id='ordinary_mob_navigation',behavior='General float/look/move/panic/follow/breed/tempt/idle tasks and spawn target selection are ordinary AI. Specific Mauler avoidance and Tuff lure extensions are separately retained. Glare hurt cancels sitting/navigation, native tame behavior; no fear/silence/stun primitive inferred. Wildfire cooldown-dependent AvoidTarget behavior changes its own ordinary navigation, not enemy control.',evidence=proof(GL,BR+'WildfireBrain',BR+'CopperGolemBrain',BR+'TuffGolemBrain',BR+'RascalBrain')),
 dict(id='summon_not_cosmetic',behavior='PlayerIllusion is a nonattacking Mob with no attack goal; ATTACK_DAMAGE attribute1 does not prove attack delivery. Illusioner decoys are real entities with bow AI. IceChunk idle counter10..20 has no gameplay read; particle/sound/animation presentation excluded except the shockwave animation length that supplies task timeout.',evidence=proof(PI,ILL,CHUNK,'common/entity/animation/WildfireAnimations')),
 dict(id='spawn_replacement',behavior='Native Illusioner replacement handles selected spawn reasons, copies equipment/flags/name and finalizes replacement. This is spawn integration, not a midcombat infection/status. Raids/patrols/biome spawning, structures, datagen, spawn eggs and profession/trade/advancement registration are excluded from mechanic counts. Zombie horse trap attack event and extra real storm lightning are separately included.',evidence=proof(EN+'event/OnEntitySpawn',REG,MX+'RaidMixin',MX+'PatrolSpawnerMixin')),
 dict(id='redstone_blocks',behavior='Copper buttons and oxidizable lightning rods extend block weathering/redstone/POI logic; do not create a custom DamageType or direct entity damage callback. Native additional storm lightning is separately cataloged. Beehives remain vanilla BeehiveBlock, eggs hatch native crabs. No new environmental DOT inferred from block names.',evidence=proof('common/init/FriendsAndFoesBlocks',MX+'LightningEntityMixin',MX+'ServerWorldMixin','common/block/CrabEggBlock')),
 dict(id='mannequin_placeholders',behavior='Version-adapter Mannequin mixin classes in this 1.21.1 build are empty placeholders targeting existing classes. No invisible combat entity or immunity inferred from their names. Mixin plugin applies normal mixins; only IntegratedServerLoader is gated on mc_runtime_test presence. Client rendering/particles/sounds/models and serializers do not introduce gameplay damage.',evidence=proof(MX+'MannequinMixin',MX+'MannequinEntityMixin',MX+'MannequinLivingEntityMixin',MX+'MannequinAvatarMixin',MX+'plugin/FriendsAndFoesMixinPlugin')),
]

def coverage():
    linked={ref['entry']:[] for e in E for ref in e['implementation']}
    for e in E:
        for ref in e['implementation']:linked[ref['entry']].append(e['id'])
    excluded={ref['entry']:[] for e in EXCLUSIONS for ref in e['evidence']}
    for e in EXCLUSIONS:
        for ref in e['evidence']:excluded[ref['entry']].append(e['id'])
    classes=[];resources=[]
    for key,w in W.items():
        entry=w['entry']
        if entry in linked:disposition='SEMANTIC_IMPLEMENTATION';reason='Exact native package/call-chain witness.'
        elif entry in excluded:disposition='EXPLICIT_EXCLUSION';reason='Owner-readable exclusion with implementation witness.'
        elif any(x in entry for x in ['/client/','/renderer/','/render/','/model/','/particle/','/animation/','/network/']):disposition='PRESENTATION_OR_SYNC';reason='Rendering, sound, animation, packet or data transport; gameplay writer/consumer covered in entity/task packages. Shockwave length explicitly retained.'
        elif any(x in entry for x in ['/worldgen/','/world/','/datagen/','/advancements/','/trades/']):disposition='ACQUISITION_OR_WORLDGEN';reason='Spawning, structures, resources, trade/reward/advancement data; no distinct combat primitive.'
        elif '/entity/ai/' in entry:disposition='ORDINARY_AI_OR_LINKAGE';reason='Native navigation, sensors, memory providers and registration; special damaging/control task callsites separately linked.'
        elif any(x in entry for x in ['/mixin/','/modcompat/','/platform/','/versions/','/events/','/init/','/config/','/util/','/tag/']):disposition='INTEGRATION_OR_REGISTRATION';reason='Version wrapper/registry/event/adapter infrastructure reviewed through the pinned registrations and all native callsites; no standalone combat mechanic inferred.'
        elif '/block/' in entry:disposition='BLOCK_UTILITY';reason='Weathering, redstone, eggs and farming; real environmental lightning separately cataloged.'
        else:disposition='SUPPORT_OR_ACQUISITION';reason='Nested data/variant/codec/entrypoint or item utility; direct combat-call frontier reviewed and linked above.'
        row=dict(entry=entry,witness_id=w['id'],disposition=disposition,reason=reason,effect_ids=sorted(set(linked.get(entry,[]))),exclusion_ids=sorted(set(excluded.get(entry,[]))))
        (classes if entry.endswith('.class') else resources).append(row)
    return dict(status='COMPLETE',classes=classes,resources=resources,scope='Every class and data JSON in installed Friends & Foes pinned. Semantic review uses implementation, registration, callers, superclass and installed resource gates; ordinary assets not counted as effects.',class_count=len(classes),resource_count=len(resources),raw_registry_custom_damage_types=[],registered_custom_effects=['friendsandfoes:reach'])

def damage_profiles():
    resources={x['entry']:x['data'] for f in ['royalvariations','friendsandfoes'] for x in read_json(OUT/'vanilla-evidence'/f'{f}.json')['resources'] if 'data' in x}
    def values(tag,seen=None):
        seen=set() if seen is None else seen
        if tag in seen:return set()
        seen.add(tag);result=set()
        for value in resources.get('data/minecraft/tags/damage_type/'+tag+'.json',{}).get('values',[]):
            value=value if isinstance(value,str) else value['id']
            result |= values(value.split(':',1)[-1][1:] if value.startswith('#:') else value.removeprefix('#minecraft:'),seen) if value.startswith('#') else {value}
        return result
    tags={k.removeprefix('data/minecraft/tags/damage_type/').removesuffix('.json'):values(k.removeprefix('data/minecraft/tags/damage_type/').removesuffix('.json')) for k in resources if '/tags/damage_type/' in k}
    result=[]
    for name in ['mob_attack','arrow','thrown','indirect_magic','magic','fireball','unattributed_fireball','freeze','lightning_bolt','on_fire']:
        rid='minecraft:'+name;members=sorted(t for t,v in tags.items() if rid in v)
        result.append(dict(id=rid,identity='VANILLA_NATIVE',custom_damage_type=False,tags=members,
            armor='BYPASSES_ARMOR' if 'bypasses_armor' in members else 'NATIVE_ARMOR',
            shield='BYPASSES_SHIELD' if 'bypasses_shield' in members else 'NATIVE_FACING_AND_SOURCE_POSITION; ownerless/no-position sources cannot be assumed blockable',
            invulnerability='BYPASS_TAG' if 'bypasses_invulnerability' in members else 'NATIVE_ADMISSION_AND_REPEAT_HIT_RULE',
            source_factory={'mob_attack':'mobAttack(livingOwner)','arrow':'arrow(arrow,owner)','thrown':'thrown(projectile,owner)','indirect_magic':'indirectMagic(chunk,owner)','magic':'magic() ownerless','fireball':'fireball(projectile,owner)','unattributed_fireball':'fireball(projectile,null)','freeze':'freeze()','lightning_bolt':'lightningBolt() ownerless','on_fire':'onFire()'}[name],
            behavior=HURT,percentage_damage='None. Wildfire shield budget threshold uses maxHP; it is not percentage target damage.',post_hit='Per package: ice freeze independent of hurt result; fireball ignite rollback on false; native bow/Blaze melee post effects retain native success gate; freeze/on_fire DOT native only.'))
    return result

def minimum_source_plan():
    """Concrete producer frontier, keeping recipients/conditions out of actor counts."""
    groups={}
    for path in P:groups.setdefault(path['fixture_family'],[]).append(path['id'])
    # A family is a native producer type/item/ambient entry point, not one spawned actor.
    definitions=[
        ('iceologer','friendsandfoes:iceologer',['iceologer'],'iceologer_spell','SlowTargetGoal requires this native caster. Ice chunks are its derived producers.'),
        ('illusioner','friendsandfoes:illusioner',['illusioner'],'illusioner_reaction','Reactive real-decoy creation requires this class; summoned clones are derived, not another independent source.'),
        ('freezing_totem','friendsandfoes:totem_of_freezing',[],'freezing_hand','The Freezing payload is selected by exact item identity.'),
        ('illusion_totem','friendsandfoes:totem_of_illusion',[],'illusion_hand','The Illusion payload is selected by exact item identity; PlayerIllusion is derived.'),
        ('crown','friendsandfoes:wildfire_crown',['crown'],'crown_tick','Refresh requires this exact head item.'),
        ('undying','minecraft:totem_of_undying',['undying'],'curios_undying','Native death-protection lookup requires this exact item, distinct from the two custom low-health items.'),
        ('wildfire','friendsandfoes:wildfire',['wildfire'],'wildfire_shield','Unique shield budget/brain tasks; debris and owned Blazes are derived producers. Disabled in pinned configuration.'),
        ('snowball','minecraft:snowball',['snowball'],'snowball_callback','The extra request is injected into native Snowball.onHitEntity, not a generic projectile callback.'),
        ('mauler','friendsandfoes:mauler',['mauler'],'mauler_feed','Enchantment reserve and burrow state require this class. Chicken/rabbit/prey are recipient controls.'),
        ('copper_golem','friendsandfoes:copper_golem',[],'copper_oxidation','Oxidation/statue state cannot be exercised by a Tuff Golem.'),
        ('tuff_golem','friendsandfoes:tuff_golem',[],'tuff_glue_sleep','Glue/custom-sleep and lure source cannot be exercised by a Copper Golem.'),
        ('glare','friendsandfoes:glare',['glare'],'glare_dark_spot','Owned dark-spot hostile reveal requires this class; tamed offspring are derived.'),
        ('rascal','friendsandfoes:rascal',['rascal'],'rascal_incoming','Unnamed three-hit disappearance requires this class.'),
        ('storm','native ServerLevel rain/thunder + enabled zombie-horse-trap entry point',['storm_trap'],'extra_lightning','Native weather roll produces lightning/trapped horse; trap/riders are derived, not injected NBT or synthetic damage.'),
        ('crab','friendsandfoes:crab',[],'type_defenses','Crab is the installed source of added arthropod/underwater-breathing tag cases; golems use a different air-supply override.')]
    sources=[]
    for key,source,owned,witness,reason in definitions:
        ids=[p['id'] for p in P if p['fixture_family'] in owned]
        if key=='freezing_totem':ids=['friendsandfoes:freezing_hand','friendsandfoes:freezing_curios']
        if key=='illusion_totem':ids=['friendsandfoes:illusion_hand','friendsandfoes:illusion_curios']
        if key=='copper_golem':ids=['friendsandfoes:'+k for k in ['copper_oxidation','copper_thunder','copper_repair','golem_source_veto']]
        if key=='tuff_golem':ids=['friendsandfoes:'+k for k in ['tuff_repair','tuff_glue_sleep','tuff_lure','golem_source_veto']]
        # type_defenses is a passive admission matrix, not a standalone attack producer.
        if key in ['iceologer','illusion_totem','wildfire','copper_golem','tuff_golem','glare','crab']:ids.append('friendsandfoes:type_defenses')
        sources.append(dict(id=key,source=source,path_ids=ids,necessity_witness_path='friendsandfoes:'+witness,necessity_reason=reason))
    return dict(unit='Distinct native producer type/item/ambient entry point. Derived entities and recipient/control permutations are not extra independent producers.',
        fixture_family_count=len(groups),fixtures=[dict(id=k,path_ids=v) for k,v in groups.items()],
        concrete_source_count=len(sources),sources=sources,
        minimality_scope='Irredundant native producer frontier for this review: each listed source has an identity-specific mechanic/path or passive-tag case that the other listed producers cannot exercise. This is not a minimum number of actors, runs, worlds or cross-mod R3 fixtures.',
        recipient_controls=['Player pre-hit HP/source/hand/Curios cases; eligible living targets, allies and nonallies.','Chicken, Rabbit, small/large Slime and baby/adult Zombie for prey predicates.','Monster versus other Enemy; current-target mobs for totem memories.','Native block/fire/fall/freeze/water/arthropod cases on the listed recipient types; spawned IceChunk and PlayerIllusion retain their own admission overrides.'],
        current_configuration_all_paths_available=False,
        restrictions=['Wildfire requires separately authorized native configuration; current enableWildfire=false. No current-instance all-path runtime cover is claimed.','Tuff-only scared TemptGoal continuation has a statically visible null-player failure path; it is a failure-case observation, not a certified successful lure.','Dormant Glare hand-heal is excluded; no tag edits authorized.'],global_minimum_status='DEFERRED_R3')

def build_review():
    groups={}
    for path in P:groups.setdefault(path['fixture_family'],[]).append(path['id'])
    return dict(schema='tno.external_effects.mod_review.v1',baseline=BASELINE,mod_key='friendsandfoes',checkpoint=CHECKPOINT,status='COMPLETE',decision='FRIENDS_AND_FOES_SEMANTIC_REVIEW_COMPLETE',starting_sha=START,
        scope='Installed Friends & Foes4.0.23, Minecraft1.21.1 and exact installed NeoForge21.1.244. Static semantic review; no runtime or pack-wide compatibility guarantee.',
        semantic_discovery_complete=True,special_damage_discovery_complete=True,source_mapping_complete=True,delivery_mapping_complete=True,semantic_effect_count=len(E),distinct_delivery_path_count=len(P),classification_counts=dict(sorted(Counter(e['primary_classification'] for e in E).items())),unresolved_native_ambiguities=[],review_required_count=0,
        effects=E,paths=P,coverage=coverage(),exclusions=EXCLUSIONS,damage_profiles=damage_profiles(),named_native_effects=['friendsandfoes:reach'],registered_combat_custom_effects=[],
        minimum_future_sources=minimum_source_plan(),
        reference_files=REFERENCES,installed_config='friendsandfoes-config-snapshot.json',compatibility_scope='Native Curios adapter included. Existing generic external hooks and full-pack mixin/tag composition remain conditional; none disabled or bypassed. Accepted Variants freeze immunity can reject DOT even after an unchecked timer write. This is not a runtime pack certification.',**boundary_flags())

def main():
    r=build_review();write_json(OUT/'mod-reviews/friendsandfoes.json',r)
    reviews=refresh(CHECKPOINT)
    prim=read_json(OUT/'behavior-primitives.json');prim.update(checkpoint=CHECKPOINT,primitives=[dict(id=e['id']+':component:'+str(i),effect_id=e['id'],mod_key=e['mod_key'],status='VERIFIED_PER_MOD',**c) for r in reviews.values() for e in r['effects'] for i,c in enumerate(e['components'])]);write_json(OUT/'behavior-primitives.json',prim)
    decision=read_json(OUT/'research-decision.json');decision.update(checkpoint=CHECKPOINT,friendsandfoes_decision=r['decision'],save_mode=False,save_reason=None,verified_per_mod_records=sum(len(r['effects']) for r in reviews.values()),next_task='Validate/protect Friends & Foes COMPLETE, then Twilight Forest semantic review only with sufficient remaining usage. Global R2 partial; R3/R4 unfinished; no runtime or production work.')
    decision['checkpoints']['R2d-complete']=START;decision['checkpoints'][CHECKPOINT]='Self: FRIENDS_AND_FOES_SEMANTIC_REVIEW_COMPLETE; exact SHA reported after live verification.';write_json(OUT/'research-decision.json',decision)
    lines=['# Friends & Foes — native semantic review','',f"Installed4.0.23 / Minecraft1.21.1 / NeoForge21.1.244. {len(E)} combat packages, {len(P)} paths; static evidence only.",'','Only registered custom MobEffect is Reach, which changes block interaction range and is excluded from combat. Wildfire is disabled in the pinned installed configuration. Tuff temptation has a statically visible null-player continuation failure case. Glare direct hand-heal contradicts its installed food tag. These facts are preserved, not patched.','',
        'Full formulas, state, source restrictions and native evidence: [review](mod-reviews/friendsandfoes.json). Damage numbers are requests, not measured HP loss.','',
        '| Mechanic | Actual behavior | Vanilla? / classification | Closest vanilla | Exact difference | Source mob/item | Delivery path | Future minimum source |','|---|---|---|---|---|---|---|---|']
    for e in E:
        cells=[e['display_name'],e['actual_behavior'].split('. ')[0]+'.',e['primary_classification'],e['closest_vanilla_equivalent'],e['vanilla_differences'],e['primary_test_source'],', '.join(x.split(':')[1] for x in e['delivery_paths']),e['primary_test_source']]
        lines.append('| '+' | '.join(str(x).replace('|','/').replace('\n',' ') for x in cells)+' |')
    lines+=['','## Classification membership','']
    for kind,count in r['classification_counts'].items():lines.append(f"- {kind} ({count}): "+', '.join(e['display_name'] for e in E if e['primary_classification']==kind)+'.')
    lines+=['','## Explicit exclusions','']+[f"- **{x['id']}**: {x['behavior']}" for x in EXCLUSIONS]
    lines+=['','## Minimum future source cover','',str(r['minimum_future_sources']['fixture_family_count'])+' local fixture families: '+', '.join(x['id'] for x in r['minimum_future_sources']['fixtures'])+'. All concrete path IDs and conditions are retained in the review; these are not numbers of gameplay runs. No gameplay was performed.','', 'Phase6/production/Stage are unchanged. No boss/L2 testing, compatibility fixes, balancing, Curve C or original Phase7. Global catalog remains PARTIAL.']
    lines+=['','Concrete native producer frontier (15): '+', '.join(x['source'] for x in r['minimum_future_sources']['sources'])+'. Derived chunks, illusions, Blazes and horse-trap riders are generated by those sources. The review maps each source to its paths and a necessity witness. This is an irredundant source frontier, not a claim about minimum gameplay runs. All-path runtime coverage is unavailable in the current configuration because Wildfire is disabled; no configuration was changed.']
    (OUT/'friendsandfoes-owner-table.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps({k:r[k] for k in ['semantic_effect_count','distinct_delivery_path_count','classification_counts']},indent=2))

if __name__=='__main__':main()
