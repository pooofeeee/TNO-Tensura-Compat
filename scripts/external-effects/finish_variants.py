"""Materialize the reviewed Variants & Ventures semantics; preserve R2b source evidence."""
from copy import deepcopy
from catalog_common import *

def component(name,implementation,formula,relation,numerical=None,binary=None):
    return dict(primitive=name,implementation=implementation,formula=formula,vanilla_relation=relation,
                numerical_parameters=numerical or {},binary_parameters=binary or [])

def build():
    old=read_json(OUT/'native-findings'/'variantsandventures.json')
    effects=deepcopy(old['findings']);byid={e['id'].split(':')[1]:e for e in effects}
    for e in effects:
        e.update(mod_key='variantsandventures',inspection_status='VERIFIED',native_status='STATIC_VERIFIED',pending=[],
            confidence='HIGH: exact source JAR, raw 1.21.1 and installed 21.1.244 code inspected; gameplay not executed.',
            existing_compat_modification='UNKNOWN',
            compat_note='Native source semantics complete. Pack-wide compatibility attribution is a separate R2h task; no global absence claim or runtime immunity guarantee.',
            reference_evidence=['native-evidence/variantsandventures.json','vanilla-evidence/variants-prerequisites.json','vanilla-evidence/vv-completion.json','reference-evidence/vv-loader-244.json'],
            implementation=[dict(entry=x['entry'],methods=x.get('methods',[])) for x in old['evidence_specifications'] if x['id'] in e['evidence_ids']],
            stacking='No custom stacks. Any MobEffectInstance uses native update/hidden-effect merging; non-effect counters are described individually.',
            removal='No custom cure hook; effect expiration/removal or native entity state processing applies.',
            damage_path=None)
    p=byid['poison_payload'];p.update(primary_classification='VANILLA_DIRECT',
        closest_vanilla_equivalent='minecraft:poison',vanilla_similarities='The actual vanilla effect, constructor and target merge/tick implementation. 100-tick amplifier-0 custom arrow payload is not divided by eight.',
        vanilla_differences='External delivery sources only. Installed NeoForge 21.1.244 selects neoforge:poison (magic fallback) whereas raw vanilla requests minecraft:magic; this is loader behavior, not a source-mod damage channel.',
        eligibility='Thicket: successful native mobAttack/Zombie hit, empty main hand, LivingEntity. Verdant: genuine native bow/Arrow, admitted arrow hurt, LivingEntity, excludes successful Enderman early-return path; post-hurt addEffect then loader MobEffectEvent.Applicable. DEFAULT calls canBeAffected; APPLY/DENY can alter admission.',
        removal='Duration expires through vanilla ticking; normal effect removal/cure paths apply. No mod-specific cure or removal hook.',
        components=[component('DOT','PoisonMobEffect.applyEffectTick / shouldApplyEffectTickThisTick','If health >1, request 1 damage; interval=max cadence(25 >> amplifier), every tick when shift result <=0.','VANILLA_DIRECT',{'payload_ticks':100,'amplifier':0,'requested_tick_damage':1,'base_interval':25},['HP >1','native effect admission'])],
        damage_path=dict(raw_vanilla_type='minecraft:magic',installed_loader_type='neoforge:poison with minecraft:magic holder fallback',
            source_mod_custom_type=False,hp='Requests damage via hurt; does not subtract HP directly.',shp='No source-mod SHP operation.',armor='Raw magic is tagged bypasses_armor.',shield='Raw magic is tagged bypasses_shield.',invulnerability='No source-mod bypass of hurt admission/cooldown; external hooks/tags remain active.',percent_health=False,max_health=False,dot=True))
    f=byid['frozen_ticks_set'];f['flags']['threshold']=True
    f.update(primary_classification='VANILLA_DIRECT',closest_vanilla_equivalent='Entity frozenTicks + LivingEntity frost/freezing + thrown-source damage',
        vanilla_similarities='Literal vanilla frozen-timer and hurt factories; no custom freezing status class.',
        vanilla_differences='Mod sets an absolute timer of 240, instead of environmental accumulation. Snowball ignores canFreeze and hurt result for assignment; melee checks both. Native speed modifier does not itself check canFreeze, but native freeze DOT does.',
        eligibility='Melee and snowball gates remain distinct. Snowball must actually reach the inherited Projectile impact callback; installed ProjectileImpactEvent may cancel impact before it. No fake source or direct call is a test substitute.',
        removal='Outside eligible powder snow, timer decays by 2 per living tick, nominally 120 ticks from 240 without refresh/reset. Eligible powder snow increments/clamps to 140. Native fire processing can clear frozen ticks. The frost attribute modifier is removed/reapplied by vanilla each living tick.',
        components=[component('FREEZE','Entity.setTicksFrozen; LivingEntity.aiStep','Assign 240; environmental update min(140,n+1) or max(0,n-2).','VANILLA_DIRECT',{'assignment':240,'threshold':140,'decay_per_tick':2},['canFreeze used by melee and DOT']),
                    component('MOVEMENT_REDUCTION','LivingEntity.tryAddFrost','MOVEMENT_SPEED ADD_VALUE = -0.05 * min(frozenTicks,140)/140, while supporting legacy block is not air and frozenTicks>0.','VANILLA_DIRECT',{'maximum_flat_reduction':0.05},['supporting block','positive timer']),
                    component('DOT','LivingEntity.aiStep','Every 40 entity ticks when fully frozen and canFreeze: request 1 freeze damage.','VANILLA_DIRECT',{'interval':40,'damage':1},['fully frozen','canFreeze']),
                    component('DIRECT_DAMAGE','GelidOnSnowballHitEvent.handleSnowballHit','Request 4 thrown damage before timer write; later Snowball callback separately requests Blaze=3/other=0.','VANILLA_DIRECT',{'mod_request':4,'vanilla_blaze_request':3,'vanilla_other_request':0})],
        damage_path=dict(raw_vanilla_types=['minecraft:thrown','minecraft:freeze'],source_mod_custom_type=False,armor='thrown uses ordinary armor; freeze bypasses armor in raw vanilla tags.',shield='thrown is ordinarily shieldable; freeze bypasses shields in raw vanilla tags.',invulnerability='Both use hurt. Timer assignment itself is not conditioned on hurt success on snowball path.',percent_health=False,max_health=False,direct_hp_subtraction=False,shp='No source-mod SHP operation.',tags=['thrown: is_projectile','freeze: is_freezing'],dot=True),
        stacking='Absolute assignment can shorten a larger existing timer. No additive stacks or custom buildup.')
    e=byid['poison_rejection'];e.update(display_name='Undead Poison/Regeneration eligibility and Thicket explicit Poison guard',primary_classification='BINARY_MECHANIC',
        closest_vanilla_equivalent='minecraft:ignores_poison_and_regen tag admission',
        actual_behavior='All four variants enter the native undead tag graph through zombie/skeleton tags and therefore default to rejecting Poison and Regeneration. Thicket additionally rejects Poison explicitly in canBeAffected; that explicit guard overlaps the default tag protection.',
        vanilla_similarities='Uses native effect-holder admission and vanilla entity-type tags.',vanilla_differences='New tagged entity types and a redundant Thicket override; loader Applicable APPLY may override DEFAULT admission.',
        numerical_parameters={},eligibility='Native canBeAffected guard under default loader event result. Effect duration and amplifier do not weaken the rejection.',
        primary_test_source='variantsandventures:thicket recipient + legitimate vanilla Poison/Regeneration delivery',
        alternate_sources=['variantsandventures:gelid','variantsandventures:murk','variantsandventures:verdant'],
        components=[component('EFFECT_IMMUNITY','LivingEntity.canBeAffected and ThicketEntity.canBeAffected','Reject Poison/Regeneration via tag graph; explicit Thicket POISON false return.','VANILLA_DIRECT',binary=['holder identity','tag membership','Applicable event result'])])
    e=byid['freeze_rejection'];e.update(primary_classification='BINARY_MECHANIC',closest_vanilla_equivalent='canFreeze and minecraft:freeze_immune_entity_types',
        vanilla_similarities='False freeze eligibility is the same native predicate used by entity tags and freeze-immune wearables.',
        vanilla_differences='Mod globally overrides Zombie freeze eligibility through its mixin hierarchy; Murk and Verdant use separate overrides. Gelid adds the native freeze-immune tag. Its builder immuneTo(POWDER_SNOW) flag makes EntityType.isBlockDangerous return false; this registration flag is not a general hurt immunity. No general immunity to arbitrary timer assignment or every frost speed modifier is implied.',
        eligibility='canFreeze gates vanilla freezing accumulation/DOT and Gelid melee timer assignment. The snowball timer write and tryAddFrost do not use that gate.',
        components=[component('FREEZE_IMMUNITY','ZombieMixin shim; MurkEntity.canFreeze; VerdantEntity.canFreeze; Gelid tag','Return false / native tag membership.','VANILLA_DIRECT',binary=['recipient class','freeze-immune entity tag'])])
    e=byid['underwater_arrow_inertia'];e.update(primary_classification='VANILLA_LIKE_EXTENDED',closest_vanilla_equivalent='AbstractArrow water velocity drag',
        vanilla_similarities='Existing native water inertia scalar multiplies velocity in the arrow tick.',vanilla_differences='0.99F when owner instanceof MurkEntity instead of vanilla 0.6F. No new source or target status.',
        eligibility='Actual AbstractArrow in water, with Murk owner. It can alter travel and consequently later impact speed; no fixed damage increase is claimed.',
        components=[component('PROJECTILE_MOTION','AbstractArrowMixin.getWaterInertia -> AbstractArrow.tick','velocity *= 0.99 instead of 0.6 in water for Murk owner.','VANILLA_LIKE_EXTENDED',{'water_retention':0.99,'vanilla_water_retention':0.6},['Murk owner','in water'])])
    e=byid['zombie_powder_snow_conversion'];e.update(primary_classification='VANILLA_LIKE_EXTENDED',closest_vanilla_equivalent='Skeleton powder-snow conversion to Stray',
        vanilla_similarities='Same 140 exposure / 300 countdown pattern, in-snow countdown, cancellation outside snow, native Mob.convertTo(...,true).',
        vanilla_differences='Applies to Zombie hierarchy and creates Gelid instead of Stray. The mod does not persist its custom exposure/countdown fields or call the installed Skeleton conversion events. Vanilla Skeleton persists StrayConversionTime and NeoForge wraps its conversion in conversion events.',
        actual_behavior=e['actual_behavior']+' Native convertTo creates a fresh entity, copies position/baby/NoAI/name/persistence/invulnerable and optionally loot/equipment/drop chances, transfers mount, then discards old entity. It does not copy HP, active effects or arbitrary persistent state. It does not call finalizeSpawn, so conversion does not itself grant Gelid the default offhand snowball. Existing main-hand equipment can prevent Gelid unarmed freeze delivery.',
        eligibility='Server, alive, AI-enabled Zombie hierarchy in powder snow. convertTo returns null if removed or entity creation fails. Gelid/Thicket inherit the global Zombie conversion path; no exclusion of already-Gelid is present in the mod method.',
        components=[component('TIMED_TRANSFORMATION','ZombieMixin.tick -> doFreezeConversion -> Mob.convertTo','Expose to 140, start at 300, decrement while in snow and convert at <0.','VANILLA_LIKE_EXTENDED',{'exposure':140,'countdown':300},['server','alive','AI enabled','powder snow','successful entity creation'])])
    for key,name,behavior,closest,impl,source,alternates,primitive in [
        ('powder_snow_walking','Gelid powder-snow walking','Gelid is appended to powder_snow_walkable_mobs. Native collision uses that predicate when above the block and not descending; falling farther than 2.5 uses the native falling collision branch. Its immuneTo(POWDER_SNOW) builder flag separately marks powder snow not dangerous in EntityType.isBlockDangerous. This is environmental traversal/hazard eligibility, not a hard movement lock or a general damage bypass.','PowderSnowBlock tag/footwear walking predicate','PowderSnowBlock.canEntityWalkOnPowderSnow / getCollisionShape; EntityType.isBlockDangerous','variantsandventures:gelid on native powder snow',[],'ENVIRONMENTAL_TRAVERSAL'),
        ('underwater_breathing','Undead underwater breathing','All four variants inherit underwater breathing through their added skeleton/zombie -> undead -> can_breathe_under_water tag graph. The direct Murk tag entry duplicates that graph. This prevents ordinary drowning-air loss; it does not grant generic damage immunity.','minecraft:can_breathe_under_water','Vanilla LivingEntity breathing and entity-type tags','variantsandventures:murk submerged',['variantsandventures:verdant','variantsandventures:gelid','variantsandventures:thicket'],'DROWNING_IMMUNITY')]:
        effects.append(dict(id='variantsandventures:'+key,display_name=name,registry_id=None,mod_key='variantsandventures',
            inspection_status='VERIFIED',native_status='STATIC_VERIFIED',primary_classification='VANILLA_DIRECT',actual_behavior=behavior,
            closest_vanilla_equivalent=closest,vanilla_similarities='Literal vanilla tag-driven mechanic.',vanilla_differences='Adds external entity types; no custom formula.',
            numerical_parameters={},scalable_parameters=[],binary_parameters=['entity-type tag membership'],
            flags=dict(uses_vanilla_mob_effects=False,custom_attributes=False,custom_entity_state=False,custom_damage_source=False,custom_stacking=False,buildup=False,threshold=False,custom_immunity_logic=False,custom_cure_logic=False,duration_matters=False,strength_matters=False),
            components=[component(primitive,impl,'Native entity-type predicate.','VANILLA_DIRECT',binary=['tag membership'])],
            primary_test_source=source,alternate_sources=alternates,delivery_paths=['vv-'+key.replace('_','-')],
            implementation=[dict(entry='data/minecraft/tags/entity_type/'+('powder_snow_walkable_mobs' if key=='powder_snow_walking' else 'can_breathe_under_water')+'.json',methods=[])],
            reference_evidence=['native-evidence/variantsandventures.json','vanilla-evidence/variants-prerequisites.json','vanilla-evidence/vv-completion.json','reference-evidence/vv-loader-244.json'],
            existing_compat_modification='UNKNOWN',compat_note='Native static semantics complete; pack-wide attribution remains R2h.',
            stacking='None',removal='Native predicate while entity type has tag; no timed state.',eligibility=behavior,damage_path=None,
            confidence='HIGH: exact source tags and vanilla/installed-loader predicates.',pending=[]))
    # Legitimate representatives preserve code paths and recipient predicates. Labels alone do not deduplicate.
    paths=[
      ('vv-thicket-melee-poison','poison_payload','MELEE','variantsandventures:thicket','Empty main hand; admitted native hit then addEffect','ThicketEntity.doHurtTarget'),
      ('vv-verdant-arrow-poison','poison_payload','PROJECTILE','variantsandventures:verdant','Native bow and Arrow; successful hurt before post-hurt effect application','VerdantEntity.getArrow -> Arrow.doPostHurtEffects'),
      ('vv-gelid-melee-freeze','frozen_ticks_set','MELEE','variantsandventures:gelid','Empty main hand; admitted hit; living canFreeze target','GelidEntity.doHurtTarget'),
      ('vv-gelid-snowball-freeze','frozen_ticks_set','THROWN_PROJECTILE','variantsandventures:gelid','Native offhand snowball is consumed by ranged goal; listener needs Gelid owner and LivingEntity','GelidSnowballRangedAttackGoal -> GelidEntity.throwSnowball -> GelidOnSnowballHitEvent'),
      ('vv-thicket-poison-eligibility','poison_rejection','OTHER','variantsandventures:thicket','Recipient of legitimate Poison and Regeneration; explicit Poison override plus tags','ThicketEntity.canBeAffected'),
      ('vv-tag-undead-eligibility','poison_rejection','OTHER','variantsandventures:murk','Recipient of legitimate Poison/Regeneration; no Thicket override','LivingEntity.canBeAffected + undead tags'),
      ('vv-zombie-freeze-eligibility','freeze_rejection','ENVIRONMENT','minecraft:zombie','Ordinary Zombie in powder snow; inherited by Gelid/Thicket','Zombie mixin canFreeze shim'),
      ('vv-murk-freeze-eligibility','freeze_rejection','ENVIRONMENT','variantsandventures:murk','Murk in powder snow','MurkEntity.canFreeze'),
      ('vv-verdant-freeze-eligibility','freeze_rejection','ENVIRONMENT','variantsandventures:verdant','Verdant in powder snow','VerdantEntity.canFreeze'),
      ('vv-gelid-tag-freeze-eligibility','freeze_rejection','ENVIRONMENT','variantsandventures:gelid','Gelid native freeze-immune type tag and powder-snow block flag coexist with Zombie shim','Gelid type registration + freeze_immune_entity_types'),
      ('vv-murk-underwater-arrow','underwater_arrow_inertia','PROJECTILE','variantsandventures:murk','Native bow arrow travels through water','AbstractArrowMixin.getWaterInertia'),
      ('vv-zombie-powder-snow-conversion','zombie_powder_snow_conversion','ENVIRONMENT','minecraft:zombie','Sustained powder-snow exposure with AI enabled','ZombieMixin.tick / Mob.convertTo'),
      ('vv-powder-snow-walking','powder_snow_walking','ENVIRONMENT','variantsandventures:gelid','Native powder snow; above surface and not descending','PowderSnowBlock.getCollisionShape'),
      ('vv-underwater-breathing','underwater_breathing','ENVIRONMENT','variantsandventures:murk','Submerge native tagged variant','LivingEntity breathing predicate')]
    pathrows=[dict(id=i,effect_ids=['variantsandventures:'+k],labels=[label],primary_source=source,setup=setup,implementation=impl,mod_key='variantsandventures',status='VERIFIED') for i,k,label,source,setup,impl in paths]
    for e in effects:e['delivery_paths']=[r['id'] for r in pathrows if e['id'] in r['effect_ids']]
    return dict(schema='tno.external_effects.mod_review.v1',baseline=BASELINE,mod_key='variantsandventures',status='COMPLETE',
        scope='Native source-mod semantic discovery/classification and source/delivery mapping; static, not gameplay or pack-interaction validation.',
        semantic_discovery_complete=True,special_damage_discovery_complete=True,source_mapping_complete=True,delivery_mapping_complete=True,
        unresolved_native_ambiguities=[],cross_mod_normalization='PENDING_R3',compat_attribution='PENDING_R2h',effects=effects,paths=pathrows,
        minimum_representatives=['minecraft:zombie','variantsandventures:gelid','variantsandventures:thicket','variantsandventures:verdant','variantsandventures:murk'],
        source_minimum_note='Five actor/entity types cover 14 preserved path/predicate cases using native attacks, powder snow, water and legitimate vanilla effect delivery. This is not five total test cases. Shared paths use different target eligibility conditions. No runtime performed.',
        exclusions=[
          'No source-mod MobEffect, custom DamageType, custom attribute, armor/Curios/skill/enchantment registry or active combat item exists; item registry is four spawn eggs and block registry empty.',
          'Murk VARIANT/SHEARED state controls skin and shear drops; own swim/navigation state is ordinary AI locomotion, not target forced movement.',
          'Natural spawn replacements, spawner pool edits, creative groups, version adapters and worldgen tags enable sources; not new target combat effects.',
          'Sounds, model/armor meshes, overlay rendering, shaking packets and advancements have no additional combat action/input hooks in this mod.',
          'Inherited Zombie burning touch remains native context: after successful hit, empty main hand + burning + random<effectiveDifficulty*0.3 ignites for 2*int(effectiveDifficulty) seconds. Not a new external implementation; retain as a confound in later source setup.',
          'Ordinary melee/arrow base damage and base mob attributes are excluded. Snowball damage request is retained as a component of its special freeze delivery.'
        ])

if __name__=='__main__':
    report=build();write_json(OUT/'mod-reviews'/'variantsandventures.json',report)
    print('Variants & Ventures COMPLETE:',len(report['effects']),'mechanic records,',len(report['paths']),'preserved paths, 5 actor representatives')
