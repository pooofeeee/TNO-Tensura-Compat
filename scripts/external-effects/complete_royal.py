"""Finalize Royal-only semantic review and shared catalog views."""
from review_royal import *
from classfile import ClassFile
import copy

CHECKPOINT='R2d-complete'
REFERENCES=['vanilla-evidence/royalvariations.json','vanilla-evidence/royal-final.json','reference-evidence/royal-loader-244.json','reference-evidence/royal-tags-244.json','vanilla-evidence/cult-completion.json','vanilla-evidence/vv-completion.json','reference-evidence/vv-loader-244.json','reference-evidence/cult-final-244.json']

def finalize():
    if any(e.get('inspection_status')=='VERIFIED' for e in E):return
    # A factory method is not evidence of a registered delivery path.
    dormant='royalvariations:dispenser_arrow'
    P[:]=[p for p in P if p['id']!=dormant]
    for e in E:
        e['delivery_paths']=[x for x in e['delivery_paths'] if x!=dormant]
        e['alternate_sources']=[x for x in e['alternate_sources'] if not x.startswith('Dispenser')]
    arrow['actual_behavior']=arrow['actual_behavior'].replace('dispenser asProjectile retains true','dormant asProjectile factory retains true; no Royal dispenser behavior is registered')
    arrow['components'][-1]['formula']='RoyalBow customArrow true; ArrowItem createArrow false; unregistered asProjectile factory defaults true'
    power['actual_behavior']=power['actual_behavior'].replace('Royal Bow is in c:tools/bows resource; exact loader TOOLS_BOW tag ID must be read, not inferred from singular constant.','Installed TOOLS_BOW is c:tools/bow (singular). Royal resource writes c:tools/bows (plural); it does not alone establish membership of the exact queried tag. Use vanilla Bow as the proven minimum source; external tag merging can widen eligibility.')
    creeper['actual_behavior']+=' RoyalSwellGoal starts at target distance<3 (or existing positive swell), continues priming only with target<=7 and LOS; navigation moves toward target instead of vanilla swell-goal stop. Ignite forces swell direction1 each entity tick.'
    creeper['components'][0]['numerical_parameters'].update(start_distance=3,continue_distance=7)
    anvil['actual_behavior']=anvil['actual_behavior'].replace('Gauntlet +2 BLOCK interaction range is utility, not entity reach.','GloveItem modifier code has a +2 BLOCK interaction range branch when this is the registered gauntlet, not entity reach; the native integration also constructs a distinct GloveItem delegate. This utility branch is excluded from combat counts.')
    for e in E:
        e.update(inspection_status='VERIFIED',unresolved_ambiguities=[],human_summary=e['actual_behavior'],reference_files=REFERENCES,
            eligibility=e['actual_behavior'],native_behavior=e['actual_behavior'])
        e.pop('pending',None)
    for path in P:path['status']='VERIFIED'

EXCLUSIONS=[
 dict(id='ordinary_stats',behavior='Base Royal Arrow damage2.4, normal Staff/Sword tier stats and armor base defense are ordinary gear properties, not new special effects. Royal Knight material helmet4/chest9/legs6/boots3,total22; toughness2.5 each,total10; base KR0. Fortitude proc is separately counted.',evidence=proof('common/items/RVTiers','common/items/armor/RVArmorMaterials','common/items/armor/RoyalKnightArmor',AR)),
 dict(id='gauntlet_block_reach',behavior='GloveItem contains +2 ADD_VALUE BLOCK_INTERACTION_RANGE for this==registered spectral_gauntlet. It is block utility, not attack reach. CuriosIntegration can register a new GloveItem delegate; no unconditional +2 equipment result claimed.',evidence=proof('common/items/GloveItem','compat/curios/CuriosIntegration')),
 dict(id='royal_bone',behavior='Guaranteed tame of nonangry untamed Wolf; native tame, target clear, sit. Acquisition/ownership utility; no independent combat buff added by item.',evidence=proof('common/items/RoyalBoneItem')),
 dict(id='bone_meal',behavior='3x3 plant growth/water-plant utility through bonemeal callbacks; no damage/effect package.',evidence=proof('common/items/RoyalBoneMealItem')),
 dict(id='telelocator',behavior='Stores target GlobalPos component, same-dimension 80-tick use then teleport and consume to empty item; particles do not damage/apply Heaviness. Utility teleport excluded.',evidence=proof('common/items/RoyalTelelocator','common/items/component/TelelocatorTracker','init/RVDataComponents')),
 dict(id='dormant_dispenser_factory',behavior='RoyalArrowItem.asProjectile can construct marking=true/no-weapon arrow, but no installed Royal registerProjectileBehavior/registerBehavior caller exists; native dispenser default drops unregistered item. Not a legitimate native producer merely because a factory exists. External registration remains outside this native claim.',evidence=proof('common/items/RoyalArrowItem')),
 dict(id='visual_state',behavior='Flash renders white/fullbright; Mark/Gaze colors and custom particles/sounds, crit-arrow particle suppression, animation states and gauntlet render are not additional damage effects. Mark glowing is retained within Mark. Gaze color alone does not force glowing.',evidence=proof('mixin/EntityRendererMixin','mixin/LivingEntityRendererMixin','mixin/AbstractArrowMixin','client/events/ClientEvents','common/effects/RVBaseEffect')),
 dict(id='attachments',behavior='rv_attachment serializes flashTick/markedTick/gazeTick, but active RVCapHelper getters/setters use IRoyalInterface SynchedEntityData, not this attachment. Mark/Gaze counters are derived each tick from actual active effects; no separate damage multiplier/state stacking.',evidence=proof('common/attachments/RVAttachment','common/attachments/RVAttachments','common/attachments/RVCapHelper','mixin/LivingEntityMixin',EV)),
 dict(id='registration_acquisition',behavior='Recipes, loot/skull drops, smithing template, spawn eggs/weights/biome selection, icons and creative tab are acquisition/registration context. No further special combat effect or custom damage type. Royal corpse spirit particles do not summon a damaging spirit.',evidence=proof('common/items/RVItems','common/items/RoyalUpgrade','common/entities/RVEntityType','common/entities/hostile/RoyalMonster',EV,'config/RVConfig')),
]

def coverage():
    t=next(t for t in read_json(OUT/'jar-inventory.json')['targets'] if t['key']=='royalvariations')
    used={r['entry'] for e in E for r in e['implementation']}
    reviewed={r['entry'] for e in EXCLUSIONS for r in e['evidence']}
    rows=[];data=[]
    with zipfile.ZipFile(t['path']) as z:
        for n in sorted(z.namelist()):
            if n.endswith('.class'):
                cls=ClassFile(z.read(n))
                if n in used:why='MECHANIC_IMPLEMENTATION'
                elif n in reviewed:why='EXPLICIT_EXCLUSION_OR_CONTEXT'
                elif n.removeprefix('com/mongoose/royalvariations/').removesuffix('.class') in W:why='REVIEWED_REGISTRATION_HELPER_OR_NESTED_SUPPORT'
                elif any(s in n for s in ['/client/','/init/']):why='VISUAL_OR_REGISTRATION_SUPPORT'
                else:raise AssertionError('Unaccounted Royal class '+n)
                rows.append(dict(entry=n,sha256=byte_hash(z.read(n)),superclass=cls.super,disposition=why))
            elif n.startswith('data/') and n.endswith('.json'):
                data.append(dict(entry=n,sha256=byte_hash(z.read(n)),disposition='REVIEWED_TAG_ACQUISITION_SPAWN_OR_CURIOS_DATA'))
        custom=[n for n in z.namelist() if '/damage_type/' in n]
    return dict(jar_sha256=t['sha256'],classes=rows,resources=data,custom_damage_types=custom,
        note='172 classes and58 data resources dispositioned; selected native method witnesses pin mechanics. No Royal custom DamageType. Utility/render/support are explicit exclusions, not effects.')

def damage_profiles():
    raw=read_json(OUT/'vanilla-evidence/royalvariations.json')
    tags={r['entry'].split('/')[-1][:-5]:r['data']['values'] for r in raw['resources'] if '/tags/damage_type/' in r['entry']}
    def values(tag,seen=None):
        seen=(seen or set())|{tag};out=set()
        for x in tags[tag]:
            if isinstance(x,dict):x=x['id']
            if x.startswith('#minecraft:'):
                sub=x.split(':')[1]
                if sub not in seen:out|=values(sub,seen)
            else:out.add(x)
        return out
    rows=[]
    for name in ['arrow','thrown','indirect_magic','explosion','player_explosion']:
        names=[k for k in tags if 'minecraft:'+name in values(k)]
        rows.append(dict(id='minecraft:'+name,tags=names,
            armor='BYPASS_ARMOR' if 'bypasses_armor' in names else 'NORMAL_NATIVE_ARMOR',
            resistance='Native Resistance/enchantment reduction retained; no bypass-resistance/effects tag for these five.',
            shield='No bypass-shield tag. Native blocking, source-position/facing and arrow-pierce rules apply; ownerless TimeBomb source has no source position so ordinary shield direction test cannot block it.',
            invulnerability='No bypass-cooldown/invulnerability tag; native rejection or excess-over-lastHurt while invulnerableTime>10. No Royal reset.',
            percentage_hp=False,fire=False,magic_identity=name=='indirect_magic'))
    return dict(types=rows,
        owner_identity={'arrow':'direct RoyalArrow, causing shooter','thrown':'direct RoyalBombProjectile/ThrownRoyalEnderPearl, causing owner','indirect_magic':'direct anvil/pearl or RoyalEnderman, causing owner/RoyalEnderman','explosion':'TimeBomb: direct=null, causing=null despite carrier used as query exclusion','player_explosion':'Bomb and RoyalCreeper native blasts: direct and causing same bomb/creeper LivingEntity; name does not imply Player owner'},
        native_blast_formula='R=2*power; exposure=seen fraction; q=(1-distance/R)*exposure; request=(q*q+q)/2*7*R+1, float (no int truncation in raw1.21.1). Native Explosion damage calculator, ignoreExplosion, events, block interaction, armor/shields apply.',
        custom_explosion_difference='Royal CustomExplosion range=given radius (not twice); queries exclude carrier/source, requires distance<=radius and nonzero eye-vector. Nonzero damage parameter is constant even when exposure0; generic damage==0 fallback int((q*q+q)/2*7*radius+1) is not used by these native producers. TimeBomb uses9; bomb/creeper status shells override explodeHurt without parent, so no hurt/push. Shells still call ignoreExplosion. Custom loop has no native ExplosionDetonate event/block damage.',
        native_post_callbacks='Arrow successful hit calls knockback, enchantment post-attack, inherited Arrow post-hurt and Mark. Royal magic paths have ordinary hurt-event processing but no explicit EnchantmentHelper post-attack call in Royal code. Bomb projectile .5 and pearl0 impacts do not gate subsequent delivery. TimeBomb ignores hurt result; anvil/pearl/splash status requires true hurt result, which need not prove HP loss on a recipient override.',
        reference_files=REFERENCES)

def compatibility():
    inv=read_json(OUT/'jar-inventory.json');candidate=[]
    for t in inv['compat_candidates']:
        hits=[]
        with zipfile.ZipFile(t['path']) as z:
            for n in z.namelist():
                if n.endswith(('.class','.json','.toml')) and any(x in z.read(n).lower() for x in [b'royalvariations',b'com/mongoose']):hits.append(n)
        candidate.append(dict(key=t['key'],sha256=t['sha256'],royal_name_hits=hits))
    old=read_json(OUT/'compat-findings/cultofazazel.json')
    keys={'antidote','devourer','cross','power','vampiric','umbrella','kitty','chorus','thorn','shock'}
    hooks=[copy.deepcopy(h) for h in old['hooks'] if h['id'] in keys]
    harmful={e['id'] for e in [dazed,rush,chosen,marked,trapped,timebomb,gaze,heavy,dark]}
    beneficial={e['id'] for e in [fort,bless,resist]}
    damage={e['id'] for e in [arrow,bomb,creeper,anvil,pearl,endsplash,timebomb]}
    for e in E:
        matching=[]
        if e['id'] in harmful:matching.append(dict(hook='antidote',predicate_match='Actual nonbeneficial effect applied to ServerPlayer; includes neutral Undead Rush only if native undead eligibility can also pass. Duration readdition can interact with net refresh and TimeBomb cancellation.'))
        if e['id'] in beneficial:matching.append(dict(hook='devourer',predicate_match='Beneficial duration instance on attacked LivingEntity; native attack/strength/equipment gates.'))
        if e['id'] in damage:
            matching += [dict(hook=k,predicate_match='Player recipient reaches native '+('death' if k=='kitty' else 'post-damage')+' callback; equipped ability/proc predicate retained. No claim that a canceled/zero hit reaches it.') for k in ['cross','kitty']]
            if e!=timebomb:
                matching += [dict(hook=k,predicate_match='Only case whose source owner is Player (arrow, Player gauntlet, pearl or bomb projectile contact). Bomb/creeper native blast owner is the Mob, never automatically the thrower.') for k in ['power','vampiric'] if e in [arrow,bomb,anvil,pearl]]
                matching += [dict(hook=k,predicate_match='Living owner/Player victim path only; exact facing/use/equipment/post-damage gates from hook. Not ownerless TimeBomb.') for k in ['umbrella','chorus','thorn','shock']]
        e['compatibility_attribution']='GENERIC_CONDITIONAL_PRESENT' if matching else 'NONE_PROVEN'
        e['compatibility_hook_ids']=[m['hook'] for m in matching]
        e['existing_compat_modification']=matching
    return dict(schema='tno.external_effects.royal_compat.v1',baseline=BASELINE,status='COMPLETE_WITH_SCOPED_ATTRIBUTION',candidate_jars=candidate,
        direct_source_specific=dict(status='NONE_PROVEN',scope='Four pinned external compatibility candidates; no Royal names/classes/resources. This is not proof of no generic behavior.'),
        hooks=hooks,per_mechanic=[dict(effect_id=e['id'],attribution=e['compatibility_attribution'],matches=e['existing_compat_modification']) for e in E],
        native_curios=dict(status='DIRECT_SOURCE_SPECIFIC',origin='Royal own integration, not external patch',implementation=proof('compat/curios/CuriosIntegration','utils/CuriosFinder','common/items/GloveItem')),
        negative_matches=['Withered Bracelet only actual WITHER: none of five Royal damage types.','Obsidian Skull only IS_FIRE: none of five Royal sources.','Cowboy Hat needs valid mounted Mob; Royal code reviewed here adds no mount interaction; not attributed without that independent prerequisite.'],
        project_context=dict(status='DIRECT_SOURCE_SPECIFIC',scope='Repository production reference only; do not conflate with installed mods',revision=START,paths=['src/main/java/com/tno/tensuracompat/compat/royalvariations/RoyalBowFirstEngraving.java','src/main/java/com/tno/tensuracompat/compat/royalvariations/RoyalVariationsGearData.java'],detail='Existing Royal Bow gear integration/first Engraving roll is locked production, already accepted. No re-research, modifications or native status scaling. No tno_tensura_compat JAR found by filename in provided instance mods; tensura_tno is a different mod.'),
        outside_scope=dict(status='UNKNOWN',detail='Full-pack dynamic composition, third-party mixins/tag reloads and gameplay results. Not an unresolved native Royal formula. No runtime certification.'))

def main():
    finalize();compat=compatibility();cov=coverage();counts=dict(sorted(Counter(e['primary_classification'] for e in E).items()))
    # Explicit local cover, not a mathematical minimum count of actors/runs.
    groups={'armor':[],'staff':[],'arrow':[],'zombie':[],'skeleton':[],'creeper':[],'bomb':[],'enderman':[],'gauntlet':[],'pearl':[],'crown':[],'shared_target_rules':[]}
    for path in P:
        k=path['id'].split(':')[1]
        group=next((g for g in ['armor','staff','crown'] if k.startswith(g)),None)
        if not group:
            group='arrow' if k in ['royal_bow_arrow','other_bow_arrow','skeleton_arrow'] else 'bomb' if k.startswith('bomb') else 'creeper' if k.startswith(('creeper','time_bomb')) else 'skeleton' if k.startswith(('skeleton','net_cut')) else 'zombie' if k.startswith(('zombie','chosen','villager')) else 'pearl' if k.startswith('pearl') else 'gauntlet' if k.startswith(('gauntlet','anvil')) else 'shared_target_rules' if k=='native_alliances' else 'enderman'
        groups[group].append(path['id'])
    minimum=dict(unit='Local fixture families with all concrete delivery cases retained; not cross-mod R3 minimization.',fixture_family_count=len(groups),fixtures=[dict(id=k,path_ids=v) for k,v in groups.items()],global_minimum_status='DEFERRED_R3')
    r=dict(schema='tno.external_effects.mod_review.v1',baseline=BASELINE,mod_key='royalvariations',checkpoint=CHECKPOINT,status='COMPLETE',decision='ROYAL_VARIATIONS_SEMANTIC_REVIEW_COMPLETE',starting_sha=START,
        scope='Installed Royal Variations2.0.4 native semantic review; raw Minecraft1.21.1 and installed NeoForge21.1.244 comparisons. Static research only.',
        semantic_discovery_complete=True,special_damage_discovery_complete=True,source_mapping_complete=True,delivery_mapping_complete=True,
        semantic_effect_count=len(E),distinct_delivery_path_count=len(P),classification_counts=counts,unresolved_native_ambiguities=[],review_required_count=0,
        effects=E,paths=P,named_native_effects=[e['registry_ids'][0] for e in E[:10]],coverage=cov,exclusions=EXCLUSIONS,damage_profiles=damage_profiles(),
        minimum_future_sources=minimum,compatibility_attribution_file='compat-findings/royalvariations.json',reference_files=REFERENCES,**boundary_flags())
    write_json(OUT/'compat-findings/royalvariations.json',compat);write_json(OUT/'mod-reviews/royalvariations.json',r)
    reviews=refresh(CHECKPOINT)
    prim=read_json(OUT/'behavior-primitives.json');prim.update(checkpoint=CHECKPOINT,primitives=[dict(id=e['id']+':component:'+str(i),effect_id=e['id'],mod_key=e['mod_key'],status='VERIFIED_PER_MOD',**c) for r in reviews.values() for e in r['effects'] for i,c in enumerate(e['components'])])
    write_json(OUT/'behavior-primitives.json',prim)
    d=read_json(OUT/'research-decision.json');d.update(checkpoint=CHECKPOINT,royal_decision=r['decision'],save_mode=False,save_reason=None,verified_per_mod_records=sum(len(r['effects']) for r in reviews.values()),next_task='Protect Royal COMPLETE with validation, commit, push and live SHA equality. Friends & Foes semantic review next; no repeat Royal/Cult/Variants. Global R2 partial, R3/R4 unfinished.')
    d.pop('usage_at_save_percent',None);d['checkpoints']['R2c3-complete']=START;d['checkpoints'][CHECKPOINT]='Self: ROYAL_VARIATIONS_SEMANTIC_REVIEW_COMPLETE; exact SHA in final local/live remote verification.';write_json(OUT/'research-decision.json',d)
    lines=['# Royal Variations — native semantics','',f'Installed2.0.4 / Minecraft1.21.1 / NeoForge21.1.244. Static only. {len(E)} packages, {len(P)} delivery cases, zero unresolved native classifications.','',
        'Exact formulas, lifecycle, compatibility predicates and evidence: [review](mod-reviews/royalvariations.json). The table keeps source packages intact; a vanilla damage identity can still occur in a custom control/status package.','',
        '| Effect / mechanic | Actual behavior | Classification | Closest vanilla | Exact difference | Composite? | Weapon/item or entity source | Paths | Future minimum source |','|---|---|---|---|---|---|---|---|---|']
    for e in E:
        vals=[e['display_name'],e['actual_behavior'].split('. ')[0]+'.',e['primary_classification'],e['closest_vanilla_equivalent'],e['vanilla_differences'],'Yes' if len(e['components'])>1 else 'No',e['primary_test_source'],str(len(e['delivery_paths'])),e['primary_test_source']]
        lines.append('| '+' | '.join(str(x).replace('|','/').replace('\n',' ') for x in vals)+' |')
    lines+=['','## Classification counts','']+[f'- {k}: {v}' for k,v in counts.items()]
    lines+=['','## Exclusions','']+[f"- {x['id']}: {x['behavior']}" for x in EXCLUSIONS]
    lines+=['','## Future test cover','',f'{len(groups)} fixture families cover all cases: '+', '.join(groups)+'. Preserve ownership, gear, target eligibility and each named delivery case in the review. This is a local source cover, not a mathematically proved minimum number of actors or runs. No runtime was performed.','', 'Phase6, production and Stage are unchanged. Friends & Foes is next only after this checkpoint is pushed and verified; no R3/R4 or new family testing.']
    (OUT/'royal-owner-table.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps(dict(effects=len(E),paths=len(P),classifications=counts,classes=len(cov['classes']),resources=len(cov['resources'])),indent=2))

if __name__=='__main__':main()
