"""Protect R2f1's inspected native contracts; do not promote unfinished semantics."""
from catalog_common import *
from classfile import ClassFile
from native_evidence import collect
from assemble_batch import refresh

START = '3f3587aed34fea3670fdcbe26c2bb1d60094023c'
CHECKPOINT = 'R2f1-partial'
NAME = 'twilightforest-r2f1-partial'


def build():
    target = next(t for t in read_json(OUT/'jar-inventory.json')['targets'] if t['key']=='twilightforest')
    assert sha256(target['path']) == target['sha256']
    selected = {
        'init/TFMobEffects': None,
        'potions/FrostedEffect': None,
        'enchantment/ApplyFrostedEffect': None,
        'init/TFDamageTypes': None,
        'util/entities/EntityExcludedDamageSource': None,
        'entity/projectile/IceArrow': None,
        'entity/projectile/TFArrow': None,
        'entity/projectile/IceBomb': None,
        'item/IceSwordItem': None,
        'item/IceBowItem': None,
        'item/IceBombItem': None,
        'init/custom/Enforcements': None,
        'util/Enforcement': None,
        'util/Restriction': None,
        'events/EntityEvents': ['entityHurts','getGearCoverage','reduceFrostedEffectIfOnFire'],
        'events/ProgressionEvents': ['performProtectionAndPortalChecks'],
    }
    specifications = []
    with zipfile.ZipFile(target['path']) as jar:
        for short, names in selected.items():
            entry = 'twilightforest/'+short+'.class'
            cls = ClassFile(jar.read(entry))
            if names is None:
                names = sorted(set(m['name'] for m in cls.methods))
            if short == 'events/EntityEvents':
                names += [m['name'] for m in cls.methods if m['name'].startswith('lambda$reduceFrostedEffectIfOnFire')]
                names += [m['name'] for m in cls.methods if any('reduceFrostedEffectIfOnFire' in str(i.get('operand')) for i in cls.instructions(m.get('code',b''))) and m['name'] not in names]
            specifications.append(dict(id='tf:'+short,mod_key='twilightforest',entry=entry,methods=names))
        resources = sorted(n for n in jar.namelist() if n.startswith('data/') and
                           ('/damage_type/' in n) and n.endswith('.json'))
        for entry in resources:
            specifications.append(dict(id='tf:data:'+entry,mod_key='twilightforest',entry=entry))
    spec = dict(schema='tno.external_effects.native_specification.v1',baseline=BASELINE,
                checkpoint=CHECKPOINT,scope='Selected Frosted contracts and native damage declarations only; no semantic closure.',
                evidence_specifications=specifications)
    write_json(OUT/'native-specifications'/f'{NAME}.json',spec)
    evidence = collect(spec)
    write_json(OUT/'native-evidence'/f'{NAME}.json',evidence)
    byid = {s['id']:s for s in specifications}

    def refs(*shorts):
        return [dict(evidence_file=f'native-evidence/{NAME}.json',witness_id='tf:'+short,
                     entry=byid['tf:'+short]['entry'],methods=byid['tf:'+short].get('methods',[])) for short in shorts]

    effect_id = 'twilightforest:frosted_package'
    paths = []
    def path(suffix,labels,source,behavior,pending,*shorts):
        paths.append(dict(id='twilightforest:frosted:'+suffix,mod_key='twilightforest',status='DRAFT',
            effect_ids=[effect_id],labels=labels,primary_source=source,setup=behavior,
            actual_native_contract=behavior,pending=pending,implementation=refs(*shorts)))
    path('ice_sword',['MELEE','ACTIVE_ITEM'],'twilightforest:ice_sword',
         'IceSwordItem.hurtEnemy returns false if super.hurtEnemy returns false; otherwise calls helper with duration200/amplifier2. This item callback is not itself proof of target.hurt success.',
         ['Trace exact installed Player/ItemStack/SwordItem callback admission; pin registry factory and all nonplayer callers.'],
         'item/IceSwordItem','enchantment/ApplyFrostedEffect')
    path('ice_arrow',['PROJECTILE','ACTIVE_ITEM'],'twilightforest:ice_bow -> IceArrow',
         'IceBowItem.customArrow wraps the parent arrow. IceArrow.onHitEntity first invokes super, then on server calls helper200/2 for any LivingEntity hit, without testing hurt return. TFArrow forwards parent doPostHurtEffects only inside the inherited post-hurt callback.',
         ['Pin installed Bow/ProjectileWeaponItem customArrow invocation, impact/parry and inherited hit admission; resolve parent tipped/spectral alternate payloads separately.'],
         'item/IceBowItem','entity/projectile/IceArrow','entity/projectile/TFArrow','enchantment/ApplyFrostedEffect')
    path('ice_bomb_contact',['THROWN_PROJECTILE'],'IceBomb contact; player item proven locally; alternate producers pending',
         'LivingEntity contact calls inflictDamage(target,2). Unless type is freeze-immune, request twilightforest:frozen for 2*(5 if freeze-hurts-extra type else1), direct entity bomb/causing entity owner, then helper200/0 regardless of hurt return. Player use consumes one item and launches speed1.25/inaccuracy1/pitch offset-5. asProjectile creates an ownerless bomb; dispenser registration and boss launch chain need final evidence.',
         ['Finish complete bomb package including inherited impact admission, source tags/mitigation, all producers and dispenser registration.'],
         'entity/projectile/IceBomb','item/IceBombItem','init/TFDamageTypes','enchantment/ApplyFrostedEffect')
    path('ice_bomb_zone',['AOE','ENVIRONMENT'],'IceBomb after block hit',
         'Block hit sets hasHit and zero motion; initial timer101 decrements each tick. Server zone processes multiples of20, including0 before discard; AABB inflated(3,2,3) excludes owner. Non-Yeti gets same request with multiplier1 and helper100/0, independent of hurt return. Yeti branch places two ice blocks and discards entity instead. These are separate package components, not proven HP damage.',
         ['Keep Yeti replacement and terrain changes in complete bomb package; validate lifecycle/repeated block hits, producer cover and exact source mitigation.'],
         'entity/projectile/IceBomb','init/TFDamageTypes','enchantment/ApplyFrostedEffect')
    path('yeti_armor_retaliation',['ARMOR_PROC'],'Living wearer with YetiArmorItem pieces; Living causing attacker',
         'EntityEvents.entityHurts(LivingDamageEvent.Post) requires nonnull causing entity and originalDamage>0. chillLevel counts nonempty armor slots whose item is YetiArmorItem. Living causing attacker gets helper(5*pieces+5,pieces,pieces>0). No extra check of final positive damage is made in this handler.',
         ['Pin event registration/lifecycle and exact Post reachability, piece item registry and generic external hooks.'],
         'events/EntityEvents','enchantment/ApplyFrostedEffect')
    path('frost_enforcement',['ENVIRONMENT'],'Progression-gated player biome enforcement',
         'Progression callback checks ServerPlayer/server level, tickCount%20==0, progression enforced, noncreative and nonspectator. Restriction lookup requires biome-key restriction and unmet required advancements. FROST consumer at tickCount%60==0 with normal tick rate directly adds Frosted100/(int)restriction.multiplier, ambient false/visible true. It does not use the helper equipment filter.',
         ['Pin listener registration, actual restriction JSON, progression predicate and advancement predicate; evaluate configuration and runtime accessibility.'],
         'events/ProgressionEvents','util/Restriction','util/Enforcement','init/custom/Enforcements')
    path('enchantment_codec',['OTHER'],'ApplyFrostedEffect enchantment entity effect; native configured source not yet resolved',
         'apply requires LivingEntity then helper(round(duration.calculate(level)),max(0,round(amplifier.calculate(level))),true). Existence of this codec is not evidence that an installed enchantment currently invokes it.',
         ['Resolve registration and data-driven producer JSON before claiming an obtainable enchantment path or counting it as final delivery.'],
         'enchantment/ApplyFrostedEffect')
    contracts = [
        'TFMobEffects registers one custom MobEffect: twilightforest:frosted; holder name FROSTY.',
        'FrostedEffect is HARMFUL and defines movement modifier twilightforest:frosted_slowdown, coefficient -0.15 ADD_MULTIPLIED_TOTAL. Native amplifier scaling makes contribution -0.15*(amplifier+1); total attributes still follow native combination/clamping.',
        'Every effect tick sets isInPowderSnow=true. If amplifier>0 and canFreeze(), assigns min(requiredFreezeTicks,currentFrozenTicks+amplifier). This is not just a renamed Slowness effect. Complete net gauge/tick-order comparison remains pending.',
        'Helper admission requires shouldHit, no freeze-immune entity tag, no freeze-immune-wearables tag in HEAD/CHEST/LEGS/FEET, and no creative Player. It does not explicitly inspect BODY, spectator or canFreeze. Native addEffect admission still applies.',
        'Incoming-damage callback skips canceled events. With Frosted and exact DamageTypes.FREEZE, replaces container newDamage with originalDamage+(float)(amplifier/2), using integer division. This does not match every freeze-like custom DamageType.',
        'Otherwise incoming IS_FIRE removes Frosted, decrements the same MobEffectInstance amplifier, then re-adds that instance if amplifier>=0. It does not require successful final HP loss. Effect removal/addition hooks and native fire immunity ordering still need final comparison.',
    ]
    effect = dict(id=effect_id,mod_key='twilightforest',display_name='Frosted status package (draft)',
        inspection_status='DRAFT',primary_classification='CUSTOM_STATUS',classification_provisional=True,
        registry_ids=['twilightforest:frosted'],actual_behavior=contracts,
        closest_vanilla_equivalent='Slowness modifier plus native powder-snow/freezing state; no direct vanilla equivalent for the entire package.',
        vanilla_similarities=['Movement coefficient/operation match Slowness; inherited effect merging, attribute lifecycle and normal cures require exact reference linkage.'],
        vanilla_differences=['Sets powder-snow flag and conditionally frozen gauge; incoming exact-freeze damage addition; incoming fire down-ranks amplifier.'],
        components=[
            dict(primitive='MOVEMENT_ATTRIBUTE',formula='-0.15*(amplifier+1), ADD_MULTIPLIED_TOTAL',vanilla_relation='Shared Slowness coefficient; distinct modifier id'),
            dict(primitive='POWDER_SNOW_STATE',formula='setIsInPowderSnow(true) each effect tick',vanilla_relation='Custom status drives native environment flag'),
            dict(primitive='FROZEN_GAUGE',formula='if amp>0 and canFreeze: min(required,current+amp)',vanilla_relation='Additional gauge assignment; net cadence pending'),
            dict(primitive='FREEZE_DAMAGE_ADJUSTMENT',formula='newDamage=originalDamage+floor(amp/2) for nonnegative amp and exact minecraft:freeze',vanilla_relation='Custom incoming-container replacement'),
            dict(primitive='FIRE_DOWNRANK',formula='remove; amp--; re-add same instance if amp>=0',vanilla_relation='Custom conditional removal/reapplication'),
        ],
        numerical_parameters={'movement_coefficient':-0.15,'effect_interval_ticks':1,'helper_sword_arrow_duration_ticks':200,'helper_sword_arrow_amplifier':2},
        scalable_parameter_candidates=['duration','amplifier','movement coefficient','freeze damage increment'],
        binary_parameters=['helper eligibility','canFreeze gate for explicit increment','exact freeze DamageType','IS_FIRE membership'],
        scalability_note='Observations only; no Stage design or balance recommendations.',
        delivery_paths=[p['id'] for p in paths],implementation=refs('init/TFMobEffects','potions/FrostedEffect','enchantment/ApplyFrostedEffect','events/EntityEvents'),
        primary_test_source='Provisional Ice Sword for eligible-target status; not a complete path cover.',
        alternate_sources=[p['primary_source'] for p in paths[1:]],
        existing_compat_modification='UNKNOWN',compat_note='Relevant pinned external hooks not yet matched to Twilight recipients/callbacks; UNKNOWN is unfinished inspection, not a native ambiguity.',
        pending=['Pin exact Minecraft1.21.1/NeoForge21.1.244 tick order, merge/cure and fire/freezing mitigation references; determine net frozen gauge cadence.',
                 'Close every producer path and source registry/config predicate; provisional codec path may be dormant.',
                 'Inspect relevant four pinned compatibility candidates and apply predicate-specific attribution.',
                 'Review all remaining mechanics before package/delivery deduplication and final fixture minimization.'],
        unresolved_ambiguities=None)
    draft = dict(schema='tno.external_effects.partial_draft.v1',baseline=BASELINE,mod_key='twilightforest',status='PARTIAL',
        checkpoint=CHECKPOINT,starting_sha=START,semantic_coverage_complete=False,promoted_to_catalog=False,effects=[effect],paths=paths)
    write_json(OUT/'partial-drafts'/f'{NAME}.json',draft)
    damage_rows = [dict(registry_id='twilightforest:'+w['entry'].split('/')[-1][:-5],data=w['data'],entry=w['entry'],entry_sha256=w['entry_sha256'])
                   for w in evidence['witnesses'] if w['entry'].startswith('data/twilightforest/damage_type/')]
    tag_rows = [dict(entry=w['entry'],data=w['data'],entry_sha256=w['entry_sha256']) for w in evidence['witnesses'] if '/tags/damage_type/' in w['entry']]
    assert len(damage_rows)==40 and len(tag_rows)==23
    resume = [
        'Start from partial-drafts/twilightforest-r2f1-partial.json and native-specifications/native-evidence of the same name. Do not redo recovery scans or the four completed reviews.',
        'Finish Frosted comparison first: exact installed Entity.baseTick/move and LivingEntity.baseTick/tick/aiStep/tickEffects ordering; incoming damage event timing, add/remove/cure/merge and armor-slot eligibility. Reuse existing raw-vanilla/loader witnesses where sufficient; pin only missing methods.',
        'Close seven draft path contracts: ice-sword native hurtEnemy admission; ice-bow customArrow and parent arrow effects; bomb contact/zone, Yeti replacement, dispenser and AlphaYeti producer; Yeti armor Post registration; progression restrictions; actual apply_frosted enchantment data/registration. Do not treat an unconfigured codec as a final source.',
        'Systematically review Naga, Lich, Minoshroom, Hydra, Knight Phantom, Ur-Ghast, Alpha Yeti, Snow Queen and every other combat-significant entity in the existing index. No boss review is closed here.',
        'Review all remaining ordinary-mob special attacks, projectile/beam/breath/summon/environment paths, boss defenses/phase admission/caps, direct HP/resource/control/AI changes.',
        'Review remaining weapons, scepters/staves, charms, armor and special items. Ice Sword/Bow/Bomb are only partially traced here; no item category is closed.',
        'Resolve all 40 damage declarations and 23 tag contributions against actual callers, raw vanilla and loader tags. A declaration is not a distinct used combat mechanic. EntityExcludedDamageSource only changes death message attribution.',
        'Match the four pinned compat candidates only to relevant Twilight predicates; record attribution, exclusions, native ambiguities if any, final components and minimum future source/path cover.',
        'Only after full semantic closure promote final records to the global views, validate all required checks and protect COMPLETE. Ice and Fire stays UNSTARTED until then.'
    ]
    note = dict(schema='tno.external_effects.partial_notes.v1',baseline=BASELINE,checkpoint=CHECKPOINT,mod_key='twilightforest',status='PARTIAL',
        starting_sha=START,jar_filename=target['filename'],jar_sha256=target['sha256'],
        save_reason='Five-hour usage reached77%; stop new research and reserve checkpoint validation/push buffer before approximately80% boundary.',
        completed_semantic_areas=['Local bytecode contracts for Frosted effect/helper, fire downrank and exact-freeze increment; selected producer bodies are preserved, not delivery closure.',
                                  '40 damage-type declarations and23 damage-tag contribution resources pinned; no claim all damage paths reviewed.',
                                  'TFDamageTypes factory delegation and EntityExcludedDamageSource death-message-only override inspected.'],
        source_factory_contract='getDamageSource passes null; getEntityDamageSource passes same entity twice; indirect helper constructs DamageSource(holder,firstEntity,secondEntity), or EntityExcludedDamageSource with optional types. First entity is direct entity; second is causing entity. Excluded types only suppress matching kill-credit entity in localized death message, not hurt admission.',
        custom_effects_found=['twilightforest:frosted'],damage_type_declarations=damage_rows,damage_tag_contributions=tag_rows,
        unreviewed_areas=resume[3:8],exact_resume=resume,
        review_required_count=0,review_required_note='No real native ambiguity established in inspected contracts. Unfinished comparisons are pending, not REVIEW_REQUIRED.',
        exclusions_inspected=[dict(area='Frosted RGB/icon and IceArrow/IceSword/IceBomb particles',reason='Presentation only; excluded from combat count.'),
                              dict(area='EntityExcludedDamageSource localized death-message selection',reason='Attribution text only; not immunity or a distinct damage mechanic.'),
                              dict(area='IceBow repair ingredient',reason='Repair/acquisition utility; not an additional attack mechanic.')],
        registered_effect_count=1,final_semantic_count=None,final_delivery_count=None,final_boss_count=None,final_item_count=None,
        draft_mechanic_count=1,draft_path_count=7,compatibility_review_status='UNFINISHED',minimum_future_source_cover=None,
        future_fixture_lower_bound=['Eligible target versus freeze-immune entity/equipment/creative controls',
            'Ice Sword callback and Ice Bow with admitted/rejected arrow damage',
            'Ice Bomb contact versus landed zone, owner exclusion and Yeti replacement',
            'Yeti armor piece-count retaliation with Living causing owner',
            'Frost restriction environmental path; configured enchantment only if producer proved',
            'Frosted amp0/1/2: native freeze ticks, exact-freeze incoming damage and fire downrank'],
        fixture_note='Provisional test dimensions, not a minimized source count or runtime execution. All boss/remaining item coverage still missing.',
        evidence_summary={'class_witnesses':len(selected),'damage_type_resources':40,'damage_tag_resources':23},**boundary_flags())
    write_json(OUT/'partial-notes'/f'{NAME}.json',note)
    review = dict(schema='tno.external_effects.mod_review.v1',baseline=BASELINE,mod_key='twilightforest',status='PARTIAL',checkpoint=CHECKPOINT,
        scope='R2f1 PARTIAL: Frosted contracts and damage declarations saved; complete semantic review pending. No draft records promoted.',
        semantic_discovery_complete=False,special_damage_discovery_complete=False,source_mapping_complete=False,delivery_mapping_complete=False,
        semantic_effect_count=0,semantic_effect_count_note='Zero finalized/promoted records; final count UNKNOWN, not absence of mechanics.',
        effects=[],paths=[],unresolved_native_ambiguities=None,remaining_native_ambiguities=None,
        ambiguity_note='Native ambiguity census is not closed. No REVIEW_REQUIRED invented for unfinished work.',
        draft_file=f'partial-drafts/{NAME}.json',notes_file=f'partial-notes/{NAME}.json',
        draft_mechanic_count=1,draft_path_count=7,exact_next_task=resume[1])
    write_json(OUT/'mod-reviews/twilightforest.json',review)
    refresh(CHECKPOINT)
    for filename in ['effect-catalog.json','effect-sources.json','delivery-path-matrix.json','vanilla-comparison.json','behavior-primitives.json']:
        obj=read_json(OUT/filename)
        obj.update(checkpoint=CHECKPOINT,unfinished_review=dict(mod_key='twilightforest',status='PARTIAL',draft_file=review['draft_file'],promoted_records=0))
        write_json(OUT/filename,obj)
    decision=read_json(OUT/'research-decision.json')
    decision.update(checkpoint=CHECKPOINT,save_mode=True,save_reason=note['save_reason'],twilightforest_decision='TWILIGHT_FOREST_SEMANTIC_REVIEW_PARTIAL',
        next_task=resume[1],recovery_twilightforest=dict(local_start=START,live_remote_start=START,working_tree_start='CLEAN',divergence='0/0',newer_work=False,restarted_research=False))
    decision['checkpoints'].update({'R2e-complete':'148a9e435b76118162695c5979f2ebce5e77307f','R2e-validator-correction':START,
                                  CHECKPOINT:'Self: partial protected after validation, commit/push and live SHA verification.'})
    write_json(OUT/'research-decision.json',decision)
    print(json.dumps(dict(native_witnesses=len(evidence['witnesses']),draft_mechanics=1,draft_paths=7,promoted=0)))


if __name__ == '__main__':
    build()
