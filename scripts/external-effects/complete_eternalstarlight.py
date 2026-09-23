"""Promote protected ES combat contracts without repeating accepted native research."""
from copy import deepcopy
from collections import defaultdict,Counter
from catalog_common import *
from assemble_batch import refresh

START='50acc9507810e634471bc94ab725e6e8da28bcf6'
CP='R2h8b-eternalstarlight-complete'
NEXT='R2i1: Bosses Rise installed-native combat foundation (block_factorys_bosses-2.1.2-neo-1.21.1.jar), then bounded combat family review. Reuse source aids, preserve accepted ES/Twilight/Ice & Fire; no runtime, L2, Stage, production or Phase6/7 work.'
STEMS=['r2h2a-crystal-numbness','r2h2b-status-control','r2h3a-energy','r2h3b-golems','r2h3c-lunar','r2h3d-soul-hunger','r2h3e-gatekeeper','r2h4a-sonar-meteor-seeds','r2h4b-ether-blade-wilt','r2h5a-native-ammo','r2h5b-special-weapons','r2h5c-armor-resources','r2h6-crests-spells','r2h7a-hazards-enchantments','r2h7b-creatures','r2h8a-closure']

# Exact pointers to reviewed facts. Grouped IDs share that fact, not necessarily a mechanic.
FACT_KEYS={}
for line in '''
crystal_infection_dot=crystal_tick shared_effect_admission damage_identity_and_mitigation
crystal_infection_status=crystal_tick crystal_melee crystal_crossbow crystal_cluster crystal_stew shared_effect_admission
crystal_cluster_damage=crystal_cluster damage_identity_and_mitigation
crystal_weapon_damage=crystal_melee crystal_crossbow
numbness_debt=numbness_admission numbness_release single_stage_boundary
crescent_cap unrealium_admission=shared_defenses
cactus_gel_cure=crystal_stew shared_effect_admission
starfire_status=starfire_trigger starfire_deliveries starfire_weapon_and_death starfire_campfire_and_boss stage_and_scope
starfire_crossbow_damage=starfire_weapon_and_death
flammable=flammable_brittle flammable_delivery
brittle=flammable_brittle brittle_delivery
whip_damage=whip_native_delivery
amaramber_arrow_damage=flammable_delivery
permafrost_damage=permafrost_cloud brittle_delivery
native_elemental_ticks=brittle_delivery flammable_delivery stage_and_scope
teary=teary_control teary_tearing
tear_bomb_damage=tear_bomb_delivery
tear_cloud_status=tear_bomb_cloud
dream_catcher=dream_catcher
sticky=sticky
oblivion=oblivion
torreya_regeneration=starfire_campfire_and_boss
energy_sparks=spark_payload spark_producers
mechanical_primary=spark_producers
ball_lightning=ball_lightning
energized_flame=energized_hazard
energy_boomerang=boomerang_primary boomerang_secondary
golem_ground_smash es_falling_debris=smash_and_debris
golem_defense golem_charge_heal=shared_boss_control golem_protection energy_blocks_charge
permafrost_melee=permafrost_native_melee
frozen_tube_damage=frozen_tube_hp frozen_tube_delivery
frozen_tube_control=frozen_tube_control frozen_tube_delivery
golem_laser=laser_payload laser_spell_path
lunar_defense=lunar_admission lunar_counterplay
lunar_bite lunar_motion lunar_native_melee=lunar_bite_and_movement lunar_thorns
lunar_breath=toxic_breath
lunar_thorns=lunar_thorns moonring_thorns
moonring_primary=moonring_thorns
lunar_spores=lunar_spores
petal_poison_cloud=petal_cloud
wand_decoy_control husk_burst=wand_and_husk
tangled_melee tangled_skull_blast=tangled_and_skulls explosion_and_stage
chain_soul_damage chain_soul_heal=chain_delivery chain_damage_and_heal chain_stage
chain_control=chain_control_lifetime
dagger_hunger_state dagger_self_damage=dagger_primary_resource native_hunger_and_scaling
dual_wield_damage=dual_wield_path
voracious_arrow=voracious_arrow
gatekeeper_admission=admission outgoing_modifier
gatekeeper_sparring=sparring_lifecycle
gatekeeper_melee=melee outgoing_modifier
gatekeeper_arrows=arrows outgoing_modifier
gatekeeper_fireball gatekeeper_explosion=fireball outgoing_modifier
gatekeeper_heal=healing
gatekeeper_teleport=teleport
solar_creeper_defense=solar_and_exclusions
moth_sonar=sonar moth_admission
moth_admission moth_healing=moth_admission
sonar_bomb=sonar_bomb
meteor_damage=meteor_payload meteor_producers natural_meteor_and_persistence
meteor_counter_resource=meteor_producers
meteor_admission=natural_meteor_and_persistence
seeds_damage=seeds_delivery seeds_payload
ether_contact_damage=ether_contact ether_deliveries
ether_corrosion=ether_corrosion ether_deliveries amulet_corrosion
thioquartz_arrow thioquartz_shard=ether_deliveries
shattered_blade=blade_delivery blade_payload
wilt_crossbow_primary wilt_aura=wilt_primary_and_aura
wilt_petal=wilt_petal
ashen_snowball ashen_control=snowball
frozen_bomb_explosion frozen_bomb_control=frozen_bomb
glacite_arrow malarite_arrow=arrow_common glacite_malarite
aethersent_arrow airsac_arrow=arrow_common aethersent_airsac
material_spears=spear_damage spear_paths
ordinary_special_weapon_hp=bows hammer scythe additional_deliveries
crescent_spin=crescent_delivery crescent_order
hammer_splash=hammer
scythe_sweep=scythe
greatsword_block=greatsword_block
flowglaze_concentration=flowglaze_concentration
warhammer_pendant=warhammer_pendant
flowglaze_arrow unrealium_crossbow=bows
flowglaze_reflection=flowglaze_shield
glacite_shield_freeze=glacite_shield
thermal_post glacite_post=material_post
material_post_poison=material_status
deepsilver_cleanse=deepsilver
armor_attributes potion_distance=armor_attributes
unrealium_attributes=unrealium_attributes unrealium_admission
unrealium_vibration=unrealium_admission
amaramber_armor=amaramber
accessory_attributes=accessory_delivery accessory_attributes
heal_multiplier=heal_fungus
armor_air=air_resources
consumable_cleanse=food_cleanse
native_food_effects=food_effects
boulders_crest=crest_passive boulders_shield selection_admission
spell_crystal_resource=spell_disposition native_delivery mana_cost selection_admission
mana_shard_refill=mana_refill
abyssal_fire=abyssal_fire abyssal_admission abyssal_touch
amaramber_fire amaramber_fire_regeneration=amaramber_fire
contact_block_hp=contact_hazards
icicle_hp=icicle
fall_cushions golem_jet=cushion_jet
abyss_air=abyss_air
glacial_sowing=freeze_enchant
fearless poisoning=other_enchants
enchantment_modifiers=enchant_disposition
aetherstrike_weather=rocket_weather
gleech_attachment=gleech_egg gleech_attachment
ordinary_creature_melee=gleech_attachment astral_golem luminofish spider thirst_walker seeker_deer registry_and_exclusions
creteor_explosion=creteor creteor_aftereffects
creteor_cloud creteor_split=creteor_aftereffects
aethersent_golem_hp aethersent_intercept=aethersent_golem
creature_heal=aethersent_golem astral_golem boarwarf stranghoul
astral_defense=astral_golem
boarwarf_alert=boarwarf
fish_poison fish_defense=luminofish
snail_defense=snail
stranghoul_vulnerability=stranghoul
spider_glow spider_defense=spider
thirst_resource=thirst_walker
native_creature_traits=registry_and_exclusions astral_golem
dusk_fire=dusk
alloy_explosion=alloy
inherited_block_hp=inherited_hazards
inherited_movement airsac_buoyancy=native_movement
weapon_physics=weapon_companions
hirer_admission=native_companion_control
native_supply_delivery=native_supply_and_fire_delivery
'''.strip().splitlines():
    names,keys=line.split('=')
    for n in names.split():FACT_KEYS['es:'+n]=keys.split()

ALIAS_GROUPS={
 'native_ammo_hp':'starfire_crossbow_damage amaramber_arrow_damage mechanical_primary moonring_primary voracious_arrow gatekeeper_arrows thioquartz_arrow wilt_crossbow_primary glacite_arrow malarite_arrow aethersent_arrow airsac_arrow flowglaze_arrow unrealium_crossbow',
 'native_explosion_hp':'tear_bomb_damage tangled_skull_blast gatekeeper_explosion frozen_bomb_explosion creteor_explosion alloy_explosion',
 'native_creature_hp':'permafrost_melee lunar_native_melee tangled_melee gatekeeper_melee ordinary_creature_melee',
 'native_heal':'chain_soul_heal golem_charge_heal gatekeeper_heal moth_healing creature_heal torreya_regeneration amaramber_fire_regeneration',
 'native_fire_freeze_ticks':'native_elemental_ticks dusk_fire',
 'native_block_contact_hp':'contact_block_hp inherited_block_hp',
 'native_consumable_cleanse':'cactus_gel_cure consumable_cleanse',
 'native_poison_tick':'tear_cloud_status',
}
ALIASES={'es:'+old:'es:'+new for new,olds in ALIAS_GROUPS.items() for old in olds.split()}
CANONICAL={
 'native_ammo_hp':('Native arrow/firework HP with preserved weapon/ammo variants','VANILLA_LIKE_EXTENDED','Once at final native AbstractArrow.onHitEntity or FireworkRocketEntity per-victim hurt after speed/base/crit/enchantment calculation. No separate projectile/base/velocity multiplier.'),
 'native_explosion_hp':('Native explosion HP with source-specific triggers','VANILLA_COMPOSITE','Once at final native Explosion per-victim hurt after radius/exposure. Preserve source holder/owner, block interaction, independent status and spawn callbacks.'),
 'native_creature_hp':('Native creature mob-attack HP','VANILLA_LIKE_EXTENDED','Once at final native mob_attack hurt after native attribute/enchantment/formula. Source-specific literal hits and successful-hit callbacks retain their contracts.'),
 'native_heal':('Native final healing, regeneration and repair','VANILLA_LIKE_EXTENDED','Once at each final LivingEntity.heal request, including native Regeneration heal1, preserving heal event/HP clamp. Chain local damage basis remains unchanged; never also scale native heal multiplier or shared damage local.'),
 'native_fire_freeze_ticks':('Native timed fire and freeze HP','VANILLA_LIKE_EXTENDED','Once at final native Entity.baseTick on_fire or LivingEntity freeze hurt; keep independent native counter/immunity/water/cadence and ownerless source.'),
 'native_block_contact_hp':('Native block-contact HP','VANILLA_DIRECT','Once at final native cactus/hot_floor/campfire hurt; preserve per-block contact/stepping/lit admission and native source.'),
 'native_consumable_cleanse':('Native consumable effect removal','VANILLA_COMPOSITE',None),
 'native_poison_tick':('Native Poison periodic HP, separate from custom ES poison','VANILLA_COMPOSITE','Once at installed PoisonMobEffect final hurt1, preserving HP>1 entry predicate and native neoforge:poison holder (magic fallback only when holder absent). Keep duration/amplifier/cadence fixed. Future Stage implementation must resolve scaled nonlethal behavior explicitly.'),
 'native_wither_tick':('Native Wither periodic HP','VANILLA_COMPOSITE','Once at native WitherMobEffect final ownerless wither1 hurt; keep40>>amplifier cadence and effect admission unchanged.'),
}
LABELS={'PASSIVE_EQUIPMENT':'PASSIVE_ITEM','PASSIVE_RESOURCE':'OTHER'}
DOWNSTREAM={
 'native_poison_tick':'petal_poison_cloud tangled_melee malarite_arrow material_spears material_post_poison native_food_effects fish_poison poisoning',
 'native_wither_tick':'wilt_aura',
 'native_fire_freeze_ticks':'thermal_post glacite_post frozen_bomb_control glacite_arrow glacite_shield_freeze glacial_sowing frozen_tube_control',
}
TYPE_CONTRACTS={
 'bite':('LunarMonstrosity.doBiteDamage:20','Lunar Monstrosity','same Monstrosity','lunar_bite'),
 'crystal_infection':('CrystalInfectionEffect periodic amplifier+1; CrystalCluster tick4','DOT:null; cluster:CrystalCluster','DOT:null; cluster:native cluster owner','crystal_infection_dot crystal_cluster_damage crystal_infection_status'),
 'dagger_of_hunger':('DaggerOfHunger.inventoryTick native resource-decay boundary3','null','null','dagger_self_damage dagger_hunger_state'),
 'electric_shock':('BallLightning beam8; ThrownEnergyBoomerang successful-primary secondary8','BallLightning or ThrownEnergyBoomerang','native projectile owner','ball_lightning energy_boomerang'),
 'energized_flame':('EnergySpark3; EnergizedFlame2; BallLightning burst8','corresponding Spark/flame/BallLightning entity','native owner of that attack entity','energy_sparks energized_flame ball_lightning'),
 'ether':('Contact .3+.6*factor where factor is0 if attribute absent, else1-ETHER_RESISTANCE, gated by armor<=0; ThioquartzShard4','contact:null; shard:ThioquartzShard','contact:null; shard:native shard owner','ether_contact_damage ether_corrosion thioquartz_shard'),
 'freeze':('PermafrostSpit1.25*owner ATTACK_SPEED or fallback15; PermafrostCloud4; FrozenTube Player6/Freeze mob configured attack/Permafrost .4*(ATTACK_DAMAGE if present else12)/other Living3','PermafrostSpit, PermafrostCloud or FrozenTube','corresponding native owner; Tube HP requires Living owner','permafrost_damage frozen_tube_damage frozen_tube_control'),
 'ground_smash':('StarlightGolemSmashPhase ownerless4','null','null','golem_ground_smash'),
 'laser':('GolemLaserBeam caster StarlightGolem4; otherwise SpellCaster3+.5*spell strength; other caster3','native RayAttack/GolemLaserBeam','native ray caster','golem_laser'),
 'meteor':('AethersentMeteor size*5*(Living owner?.08:1)*(Player owner?configured player modifier:1)','native meteor owner, not meteor projectile; null when absent','same native meteor owner/null; saved owner loss remains native','meteor_damage meteor_admission'),
 'numbness':('Stored NUMBNESS_DAMAGE debt accumulated .75*parent Pre amount; release full saved debt when effect absent','null','null','numbness_debt crescent_cap'),
 'poison':('Toxic breath3; LunarThorn mode0=4/other=3; LunarSpore5; PoisonousCloud5; TangledHusk10','respective breath/thorn/spore/cloud attack entity; Husk burst uses its owner as direct entity','native attack owner; Husk same owner as direct','lunar_breath lunar_thorns lunar_spores petal_poison_cloud husk_burst'),
 'seeds':('ShotSeeds .5 native seedDamage passed through enchantment modification, plus current velocity length*1.25, then native ammo multiplier','ShotSeeds','native projectile owner','seeds_damage'),
 'shattered_blade':('ThrownShatteredBlade current Living owner ATTACK_DAMAGE if attribute present else5, then weapon enchant modifyDamage; no speed/base/arrow-crit term','ThrownShatteredBlade','native owner or blade itself when owner absent','shattered_blade'),
 'sonar':('CrystallizedMoth current ATTACK_DAMAGE *4 if target #vulnerable_to_sonar_bomb else1','CrystallizedMoth','same Moth, not tame owner','moth_sonar moth_admission'),
 'soul_absorb':('ChainOfSouls configured soulAbsorbDamage (native default and pinned snapshot2) through native weapon enchantment modification','ChainOfSouls','Player owner required for actual HP path','chain_soul_damage chain_soul_heal chain_control'),
 'starfire':('ESCommonHandler Post amount/3 when native Starfire branch admits; recursive same-type guard retained','original parent source direct entity','original parent source causing entity','starfire_status'),
 'wilt':('WiltedPetal8','WiltedPetal','native projectile owner','wilt_petal wilt_aura'),
}

def unique(rows):
    out=[];seen=set()
    for r in rows:
        k=json.dumps(r,sort_keys=True)
        if k not in seen:out.append(deepcopy(r));seen.add(k)
    return out

def implementation(d):
    watched=defaultdict(set)
    for r in read_json(OUT/'eternalstarlight-combat-closure-census.json')['watched_methods']:watched[r['entry']].add(r['method'])
    refs=[]
    for ref in d['reference_files']:
        f=ref['file']
        if not f.startswith('native-evidence/'):continue
        for w in read_json(OUT/f)['witnesses']:
            allnames={m['name'] for m in w.get('methods',[])};methods=sorted(allnames & watched[w['entry']])
            # Resource/spell/attribute packages legitimately lack direct hurt.
            if not methods:methods=sorted(n for n in allnames if n in {'tick','use','releaseUsing','onUseTick','onPostLivingHurt','onLivingHeal','getDefaultAttributeModifiers','forEachModifier','apply','canCast','castTick','start','stop','canUse','onEntityTick','getGravity','scaleKnockback','getHeldProjectile'})
            if methods:refs.append(dict(evidence_file=f,witness_id=w['id'],entry=w['entry'],methods=methods))
    assert refs,d['checkpoint']
    return unique(refs)

def source_coverage(sections):
    from collect_eternalstarlight_foundation import ES,FACTORY
    census=read_json(OUT/'eternalstarlight-source-census.json');tags=read_json(OUT/'eternalstarlight-damage-tags.json');watch=read_json(OUT/'eternalstarlight-combat-closure-census.json')
    evidence={};section_by_evidence=defaultdict(list)
    for stem,d in sections.items():
        # First native witness file is the section's own review, not a shared prerequisite.
        own=next(r['file'] for r in d['reference_files'] if r['file'].startswith('native-evidence/'))
        section_by_evidence[own].append('eternalstarlight-'+stem+'.json')
    for f in sorted((OUT/'native-evidence').glob('eternalstarlight-*.json')):
        for w in read_json(f)['witnesses']:
            for m in w.get('methods',[]):evidence.setdefault((w['entry'],m['name'],m['descriptor']),[]).append(dict(evidence_file='native-evidence/'+f.name,witness_id=w['id'],entry=w['entry'],methods=[m['name']]))
    def references(row):
        refs=evidence[(row['entry'],row['method'],row['descriptor'])]
        semantic=unique([s for r in refs for s in section_by_evidence[r['evidence_file']]])
        return dict(implementation=refs,semantic_sections=semantic or ['eternalstarlight-r2h8a-closure.json'])
    factory={(r['entry'],r['method'],r['descriptor']) for r in census['factory_callers']}
    types=[]
    for d in tags['declarations']:
        key=d['id'].split(':')[1].upper();refs=[]
        for row in census['damage_key_references']:
            if not any(str(h['operand']).startswith(FACTORY+'.'+key+'L') for h in row['hits']):continue
            isfactory=(row['entry'],row['method'],row['descriptor']) in factory
            kind='ACTUAL_NATIVE_DAMAGE_FACTORY_CALLER' if isfactory else 'DATAGEN_ONLY_NOT_DELIVERY' if '/datagen/' in row['entry'] else 'ADMISSION_ONLY_NOT_DELIVERY'
            refs.append(dict(entry=row['entry'],method=row['method'],descriptor=row['descriptor'],kind=kind,**(references(row) if '/datagen/' not in row['entry'] else {})))
        assert any(r['kind']=='ACTUAL_NATIVE_DAMAGE_FACTORY_CALLER' for r in refs),d['id']
        short=d['id'].split(':')[1];formula,direct,causing,packages=TYPE_CONTRACTS[short];packageids=['es:'+n for n in packages.split()];contracts=[];deliveries=[]
        for stem,section in sections.items():
            for package in section['mechanic_packages']:
                if package['id'] not in packageids:continue
                for k in FACT_KEYS[package['id']]:contracts.append(dict(section='eternalstarlight-'+stem+'.json',fact_key=k,text=section['facts'][k]))
                deliveries+=package['delivery_paths']
            for extension in section.get('existing_package_deliveries',[]):
                if extension['package_id'] in packageids:deliveries+=extension['delivery_paths']
        types.append(dict(**d,disposition='USED',requested_amount_formula=formula,direct_entity=direct,causing_entity=causing,callers=refs,mechanic_ids=unique([ALIASES.get(x,x) for x in packageids]),delivery_paths=unique(deliveries),armor_behavior='BYPASSES_ARMOR' if 'minecraft:bypasses_armor' in d['tags'] else 'Native armor processing retained; no bypass_armor tag.',shield_behavior='BYPASSES_SHIELD' if 'minecraft:bypasses_shield' in d['tags'] else 'Native source-position/direction/piercing/blocking admission retained; no bypass_shield tag.',resistance_behavior='BYPASSES_RESISTANCE' if 'minecraft:bypasses_resistance' in d['tags'] else 'Native Resistance processing retained; no bypass_resistance tag.',protection_behavior='BYPASSES_ENCHANTMENTS' if 'minecraft:bypasses_enchantments' in d['tags'] else 'Native protection/enchantment processing retained; no bypass_enchantments tag.',hurt_return_dependencies_and_secondary_callbacks=unique(contracts),scope='Tags are scoped raw Minecraft + installed loader + ES contributions; runtime pack tag merges and generic Tensura/L2 interception unmeasured. Amount/control/source contracts inlined from protected family evidence.'))
    utilities=['/LootChestBlockEntity.','/LootBagItem.','/EyeOfSeeking.','/CrestEntity.','/SoulitSpectator.']
    methods=[]
    for r in watch['watched_methods']:
        short=r['entry'];utility=any(x in short for x in utilities) or (short.endswith('/ESEntityUtil.class') and r['method']=='givePlayerItem') or (short.endswith('/ESBoss.class') and r['method']=='trySpawnLoot') or (short.endswith('/EthericEyeItem.class'))
        methods.append(dict(**r,disposition='UTILITY_EXCLUDED_NO_SEPARATE_COMBAT_PACKAGE' if utility else 'REVIEWED_NATIVE_COMBAT_OR_SHARED_ADMISSION_HELPER',**references(r)))
    return dict(schema='tno.external_effects.es_total_source_coverage.v1',baseline=BASELINE,checkpoint=CP,installed_jar_sha256=tags['archives'][-1]['sha256'],custom_damage_types=types,factory_caller_count=len(factory),watched_methods=methods,whole_class_inventory='eternalstarlight-combat-closure-census.json',scope='Total actual custom source caller map and watched-method dispositions; inherited source variants and semantic exclusions remain in each protected section, not inferred solely from census.',direct_compat='eternalstarlight-direct-compat-census.json',runtime_tests=0)

def build():
    sections={s:read_json(OUT/('eternalstarlight-'+s+'.json')) for s in STEMS};groups=defaultdict(list);origpaths={};pathgroups=defaultdict(set);dispositions=[];manifest_sections=[];fixture_sets=[]
    for stem,d in sections.items():
        filename='eternalstarlight-'+stem+'.json';impl=implementation(d)
        manifest_sections.append(dict(file=filename,sha256=sha256(OUT/filename),packages=len(d['mechanic_packages']),paths=len(d['delivery_paths'])))
        fixture_sets.append(dict(file=filename,contracts=deepcopy(d['unexecuted_future_fixtures']),runtime_status='NOT_RUN'))
        for p in d['delivery_paths']:
            assert p['id'] not in origpaths,p['id'];origpaths[p['id']]=(filename,deepcopy(p),impl)
        for m in d['mechanic_packages']:
            target=ALIASES.get(m['id'],m['id']);facts=[dict(file=filename,key=k,text=d['facts'][k]) for k in FACT_KEYS[m['id']]]
            groups[target].append(dict(section=filename,original=deepcopy(m),facts=facts,implementation=impl))
            dispositions.append(dict(section=filename,original_id=m['id'],canonical_ids=[target],status='ALIASED_NATIVE_PRIMITIVE' if target!=m['id'] else 'RETAINED_NATIVE_CONTRACT'))
            for pid in m['delivery_paths']:pathgroups[pid].add(target)
    extensions=[]
    for stem,d in sections.items():
        for x in d.get('existing_package_deliveries',[]):
            target=ALIASES.get(x['package_id'],x['package_id']);assert target in groups
            for pid in x['delivery_paths']:assert pid in origpaths;pathgroups[pid].add(target)
            extensions.append(dict(origin_section='eternalstarlight-'+stem+'.json',**x,canonical_id=target))
    downstream=[]
    for target,names in DOWNSTREAM.items():
        target='es:'+target
        for stem,d in sections.items():
            for m in d['mechanic_packages']:
                if m['id'].split(':')[1] not in names.split():continue
                parent=next(x for x in groups[ALIASES.get(m['id'],m['id'])] if x['original']['id']==m['id']);member=deepcopy(parent)
                if m['id']=='es:tangled_melee':member['original']['delivery_paths']=['es:lunar:tangled_melee']
                groups[target].append(member)
                for pid in member['original']['delivery_paths']:pathgroups[pid].add(target)
                next(x for x in dispositions if x['original_id']==m['id'])['canonical_ids'].append(target)
                downstream.append(dict(original_id=m['id'],canonical_id=target,delivery_paths=member['original']['delivery_paths'],condition='Only after the native qualifying status/counter was applied; Poison food subcase is Cactus Fruit. This is an independent later native request, never a multiplier on the delivery/status wrapper.'))
    paths=[];fixtures=[]
    for pid,(filename,p,impl) in origpaths.items():
        assert pathgroups[pid],('Unmapped native path',pid)
        labels=[LABELS.get(v,v) for v in p['labels']];assert set(labels)<=set(DELIVERIES)
        source=p.get('native_path',p.get('source',pid));controls=p.get('runtime_variants',[])
        row=dict(id=pid,mod_key='eternalstarlight',status='VERIFIED',inspection_status='VERIFIED',labels=labels,effect_ids=sorted(pathgroups[pid]),primary_source=source,setup='Genuine native delivery: '+str(source),implementation=impl,native_contract=p,semantic_section=filename,fixture_controls=controls,source_case_ids=[pid],runtime_status='NOT_RUN')
        paths.append(row);fixtures.append(dict(path_id=pid,effect_ids=row['effect_ids'],primary_source=source,native_contract=p,section_fixture_set=filename,controls=controls,runtime_status='NOT_RUN'))
    effects=[]
    for eid,members in groups.items():
        base=members[0]['original'];name,cl,point=CANONICAL.get(eid.split(':')[1],(base['name'],base['primary_classification'],base['single_scaling_point']))
        scale=bool(point);categories=unique([c for member in members for c in member['original']['tno_categories']]);categories=[c for c in categories if c not in {'NUMERIC_SCALABLE','NO_STAGE_VALUE'}]+['NUMERIC_SCALABLE' if scale else 'NO_STAGE_VALUE']
        facts=unique([f for member in members for f in member['facts']]);variants=[dict(section=m['section'],original_package_id=m['original']['id'],native_contract=m['original'],fact_keys=[f['key'] for f in m['facts']]) for m in members]
        deliveries=[p['id'] for p in paths if eid in p['effect_ids']];assert deliveries
        reason=base.get('stage_reason','Native eligibility and companion state remain unchanged.')
        components=[dict(primitive='NATIVE_FINAL_AMOUNT' if scale else 'NATIVE_CONTROL_ADMISSION_RESOURCE',formula=point or reason,numerical_parameters={'source_variant_contracts':[v['section']+'#'+v['original_package_id'] for v in variants]},binary_parameters=['Keep exact native source, owner, immunity, mitigation and hurt-return ordering.'],vanilla_relation=cl,tno_categories=categories,stage_scaling_needed=scale,single_scaling_point=point)]
        if scale and 'COMPOSITE' in categories:components.append(dict(primitive='UNSCALED_NATIVE_COMPANIONS',formula='Native ratios/attributes/counters/radius/cadence/control and admission remain unscaled; no duplicate Stage multiplier.',numerical_parameters={},binary_parameters=[],vanilla_relation='Source-specific native companions',stage_scaling_needed=False,single_scaling_point=None))
        refs=unique([r for m in members for r in m['implementation']]);behavior=[f['text'] for f in facts]
        effects.append(dict(id=eid,mod_key='eternalstarlight',display_name=name,human_summary=name+'; native static contract, runtime untested.',inspection_status='VERIFIED',native_status='STATIC_VERIFIED',primary_classification=cl,classification_provisional=False,registry_ids=[],tno_categories=categories,stage_scaling_needed=scale,single_scaling_point=point,stage_reason=reason,actual_behavior=behavior,fact_references=[dict(file=f['file'],key=f['key']) for f in facts],components=components,implementation=refs,delivery_paths=deliveries,primary_test_source=next(p['primary_source'] for p in paths if p['id']==deliveries[0]),alternate_sources=unique([p['primary_source'] for p in paths if eid in p['effect_ids']]),source_parameter_variants=variants,closest_vanilla_equivalent=cl+'; exact delegated callbacks in source contracts.',vanilla_similarities=['Native hurt/heal/status/source admission retained where actually delegated.'],vanilla_differences=behavior,compatibility_attribution='SCOPED_EXPLICIT_NAME_SCAN_AND_GENERIC_HOOKS_STATIC_ONLY',compatibility_evidence=['eternalstarlight-r2h1-source-foundation.json','eternalstarlight-r2h8a-closure.json'],pending=[],unresolved_ambiguities=[],runtime_status='NOT_RUN'))
    counts=dict(input_packages=len(dispositions),native_cases=len(origpaths),final_mechanics=len(effects),final_deliveries=len(paths),aliased_input_packages=sum(x['status']=='ALIASED_NATIVE_PRIMITIVE' for x in dispositions),delivery_extensions=len(extensions),excluded_combat_cases=0)
    manifest=dict(schema='tno.external_effects.es_promotion_map.v1',baseline=BASELINE,checkpoint=CP,starting_sha=START,sections=manifest_sections,mechanic_dispositions=dispositions,path_dispositions=[dict(original_id=p['id'],canonical_id=p['id'],canonical_effect_ids=p['effect_ids']) for p in paths],delivery_extensions=extensions,downstream_native_amounts=downstream,counts=counts,dedup_policy='Shared native arrow/firework, explosion, mob-attack, healing, timed fire/freeze, block contact and consumable cleanse consolidated; every native source/control/defense path retained. Existing status delivery and later native DOT are separate records. Cross-mod R3 normalization remains pending.',label_normalization=LABELS,native_effect_reference_files=[dict(file=f,sha256=sha256(OUT/f)) for f in ['reference-evidence/vv-loader-244.json','vanilla-evidence/iceandfire-cockatrice.json','vanilla-evidence/iceandfire-ghost-troll.json']])
    matrix=dict(schema='tno.external_effects.es_future_fixtures.v1',baseline=BASELINE,checkpoint=CP,status='FUTURE_ONLY_NOT_RUN',fixtures=fixtures,section_fixture_sets=fixture_sets,runtime_tests=0,note='Every protected fixture and native delivery retained; not a globally minimized count. No synthetic events, source replacement or forced ineligible payloads.',**boundary_flags())
    review=dict(schema='tno.external_effects.mod_review.v1',baseline=BASELINE,mod_key='eternalstarlight',checkpoint=CP,starting_sha=START,status='COMPLETE',decision='ETERNAL_STARLIGHT_COMBAT_SEMANTIC_REVIEW_COMPLETE',scope='Installed Eternal Starlight0.8.1 combat-significant static semantics complete. Utility/render/acquisition excluded briefly; whole-pack runtime compatibility and Stage implementation untested.',semantic_discovery_complete=True,special_damage_discovery_complete=True,source_mapping_complete=True,delivery_mapping_complete=True,effects=effects,paths=paths,semantic_effect_count=len(effects),unresolved_native_ambiguities=[],remaining_native_ambiguities=[],review_required=[],classification_counts=dict(Counter(e['primary_classification'] for e in effects)),promotion_manifest='eternalstarlight-final-promotion-map.json',future_runtime_fixture_matrix='eternalstarlight-future-runtime-fixtures.json',whole_source_closure='eternalstarlight-total-source-coverage.json',exact_next_task=NEXT,runtime_tests=0,**boundary_flags())
    return review,manifest,matrix,source_coverage(sections)

def save():
    r,m,f,c=build()
    for name,obj in [('mod-reviews/eternalstarlight.json',r),('eternalstarlight-final-promotion-map.json',m),('eternalstarlight-future-runtime-fixtures.json',f),('eternalstarlight-total-source-coverage.json',c)]:write_json(OUT/name,obj)
    refresh(CP);p=read_json(OUT/'behavior-primitives.json');p['primitives']=[x for x in p['primitives'] if x['mod_key']!='eternalstarlight']
    for e in r['effects']:
        for i,component in enumerate(e['components']):p['primitives'].append(dict(component,id=e['id']+':component:'+str(i),effect_id=e['id'],mod_key='eternalstarlight',status='VERIFIED_PER_MOD',implementation=e['implementation'],source_case_paths=e['delivery_paths']))
    p.update(checkpoint=CP);write_json(OUT/'behavior-primitives.json',p)
    for name in ['effect-catalog.json','effect-sources.json','delivery-path-matrix.json','vanilla-comparison.json','behavior-primitives.json']:
        o=read_json(OUT/name);o.pop('unfinished_review',None);o['last_completed_mod']='eternalstarlight';write_json(OUT/name,o)
    o=read_json(OUT/'research-decision.json');o.update(checkpoint=CP,next_task=NEXT,latest_eternalstarlight_subsection_decision=r['decision'],save_mode=False,save_reason=None);o['checkpoints']['R2h8a-combat-closure-complete']=START;o['checkpoints'][CP]='Self: exact SHA from commit/live verification.';write_json(OUT/'research-decision.json',o)
    lines=['# Eternal Starlight combat owner table — COMPLETE','',f"{len(r['effects'])} reviewed combat packages and {len(r['paths'])} native source/control/defense contracts promoted from {m['counts']['input_packages']} protected input packages. Static evidence only; runtime tests remain unexecuted.",'','All18 custom DamageTypes have actual native caller mappings. Nine effects and native immunity, ownership, direct/causing identity, return-value gates, loader processing, resource and control prerequisites are retained. Eight registered spell stubs have no damage payload. Numbness debt and derived Starfire damage must not receive a second Stage multiplier.','', '| Mechanic | TNO classification | Single candidate Stage boundary / no-value reason |','|---|---|---|']
    for e in r['effects']:lines.append('| '+e['display_name']+' | '+', '.join(e['tno_categories'])+' | '+str(e['single_scaling_point'] or e['stage_reason']).replace('|',' / ')+' |')
    lines+=['','[Complete accepted contracts](mod-reviews/eternalstarlight.json), [every native path and fixture](eternalstarlight-future-runtime-fixtures.json), [total source coverage](eternalstarlight-total-source-coverage.json), [deduplication map](eternalstarlight-final-promotion-map.json).','','Runtime priorities: native source tags versus visual elements; parent/derived amount handling; body/arrow/firework/ownerless routes; rejected HP versus independent status/control/spawns; target/mount/effect/guard admission; actual final healing and shared local damage bases. Resistance/Nullification/L2 behavior is unmeasured. Native Poison HP>1 admission and future scaled nonlethal policy need explicit runtime/implementation review; no status duration/amplifier or radius/count scaling is proposed.','','Short exclusions: rendering/cosmetics, crafting/acquisition/progression, storage/information, ordinary self utility, passive creatures with no attack callback, worldgen without combat effect. No runtime, L2, production, Stage, Phase6 or Phase7 work.','','Exact next task: '+NEXT,'']
    (OUT/'eternalstarlight-final-owner-table.md').write_text('\n'.join(lines),encoding='utf-8')
    main=ROOT/'docs/external-effects-catalog-research.md';s=main.read_text(encoding='utf-8');heading='## R2h8b — Eternal Starlight combat catalog COMPLETE'
    if heading not in s:s+='\n'+heading+'\n\n'+f"{len(r['effects'])} deduplicated packages and {len(r['paths'])} native paths, all18 DamageTypes mapped; no runtime compatibility certification. [Owner table and exact next task](benchmarks/external-effects-catalog/eternalstarlight-final-owner-table.md).\n"
    main.write_text(s,encoding='utf-8');print(json.dumps(m['counts'],indent=2))
if __name__=='__main__':save()
