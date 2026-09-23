"""Whole Twilight static closure: explicit source dispositions, no extra mechanics."""
from twilight_evidence import *
from twilight_damage_closure import census as damage_census
BATCH='twilight-global-closure'
TOKENS=['.hurt(','.heal(','.setHealth(','.setAbsorptionAmount(','.causeFallDamage(','.igniteForSeconds(','.setRemainingFireTicks(','.addEffect(','.removeEffect(','.removeAllEffects(','.setTicksFrozen(','.setAirSupply(','.setTarget(','.knockback(','.push(','.setDeltaMovement(','.addPermanentModifier(','.addTransientModifier(','.removeModifier(','.setBaseValue(','.explode(','.addFreshEntity(','.addFreshEntityWithPassengers(','.tryAddFreshEntityWithPassengers(','.startRiding(','.stopRiding(','.spawn(','.doHurtTarget(','.setNoAi(','.setInvulnerable(','.teleportTo(','.randomTeleport(']
EXCLUDED={
 'entity/boss/IBossLootBuffer':{'saveDropsIntoBoss':'Native loot buffering/overflow ItemEntity; acquisition, not a summoned combatant.'},
 'item/MagicPaintingItem':{'useOn':'Native painting placement; decoration.'},
 'block/FireflySpawnerBlock':{'useItemOn':'Particle radius configuration and returned Firefly ItemEntity; not hostile/entity fire spawning.'},
 'block/HorizontalHollowLogBlock':{'useItemOn':'Log moss/snow/ladder decoration and returned ItemEntity.'},
 'block/ClimbableHollowLogBlock':{'useItemOn':'Sheared decorative contents returned as ItemEntity.'},
 'block/TrollRootBlock':{'useWithoutItem':'Harvested root ItemEntity.'},
 'block/LiverootBlock':{'useItemOn':'Harvested liveroot ItemEntity.'},
 'block/TorchberryPlantBlock':{'useWithoutItem':'Harvested torchberry ItemEntity.'},
 'world/components/feature/MonolithFeature':{'place':'Raven placement; passive worldgen, protected Raven behavior reused.'},
 'world/components/structures/darktower/DarkTowerMainComponent':{'placeItemFrameRotated':'Native ItemFrame decoration.'},
 'world/components/structures/finalcastle/FinalCastleBossGazeboComponent':{'willBeAddingFinalBossSoon':'Native WIP text and Interaction display; does not spawn final boss.'},
 'world/components/structures/lichtowerrevamp/LichTowerMagicGallery':{'handleDataMarker':'Magic painting placement/variant selection; protected combat room markers handled elsewhere.'},
 'world/components/structures/TFStructureComponent':{'setInvisibleTextEntity':'TextDisplay presentation.','setDebugEntity':'Invisible/noAI/invulnerable debug Sheep marker, not native encounter production.'},
 'command/TFTeleportCommand':{'run':'Administrative teleport utility, no combat callback or source.'},
 'util/DisplayUtil':{'spawnBlockDisplay':'Debug BlockDisplay.','setTextEntity':'Debug TextDisplay.'},
 'util/entities/EntityUtil':{'tryHangPainting':'Native painting placement, not combat entity production.'},
 'util/entities/EntityRenderingUtil':{'lambda$fetchEntity$0':'NoAI display entity cache for rendering; not server attack production.'}}


def api_census(target):
    known={}
    for p in sorted((OUT/'native-evidence').glob('*.json')):
        for w in read_json(p).get('witnesses',[]):
            if w.get('mod_key')!='twilightforest':continue
            for m in w.get('methods',[]):known.setdefault((w['entry'],m['name'],m['descriptor']),[]).append(dict(evidence_file='native-evidence/'+p.name,witness_id=w['id']))
    records=[];class_count=0
    with zipfile.ZipFile(target['path']) as jar:
        for entry in jar.namelist():
            if not entry.startswith('twilightforest/') or not entry.endswith('.class'):continue
            b=jar.read(entry);cl=ClassFile(b);class_count+=1
            for m in cl.methods:
                hits=[i for i in cl.instructions(m.get('code',b'')) if any(t in str(i['operand']) for t in TOKENS)]
                if not hits:continue
                refs=known.get((entry,m['name'],m['descriptor']),[]);assert refs,(entry,m['name'])
                reason=EXCLUDED.get(entry[len('twilightforest/'):-6],{}).get(m['name'])
                records.append(dict(entry=entry,method=m['name'],descriptor=m['descriptor'],class_sha256=byte_hash(b),hits=hits,implementation=refs,disposition='EXCLUDED_NONCOMBAT' if reason else 'PROTECTED_NATIVE_WITNESS',reason=reason or 'Reuses protected semantic owner review and explicit source/exclusion dispositions; witness presence alone is not the semantic conclusion.'))
    return dict(schema='tno.external_effects.twilight_global_source_census.v1',baseline=BASELINE,jar_sha256=target['sha256'],class_count=class_count,method_hit_count=len(records),scope='Whole installed outer-class exact API-call census supplements, rather than replaces, protected semantic discovery, registry/inheritance review, JSON source maps and all31 nested transformers. Zero new combat-significant owners remain after explicit dispositions.',tokens=TOKENS,records=records)



def compat_census():
    import zlib
    inv=read_json(OUT/'jar-inventory.json');rows=[]
    for target in [next(t for t in inv['targets'] if t['key']=='twilightforest')]+inv['compat_candidates']:
        needles=['tensura','l2hostility','l2complements','l2library','dev/xkmc/'] if target['key']=='twilightforest' else ['twilightforest','twilight_forest']
        hits=[]
        with zipfile.ZipFile(target['path']) as jar:
            for entry in jar.namelist():
                if entry.endswith('/') or entry.endswith('.jar'):continue
                raw=jar.read(entry);b=zlib.decompress(raw,31) if raw.startswith(b'\x1f\x8b') else raw
                matched=[n for n in needles if n.encode() in b.lower() or n in entry.lower()]
                if matched:hits.append(dict(entry=entry,needles=matched,sha256=byte_hash(raw)))
        rows.append(dict(mod_key=target['key'],jar_sha256=target['sha256'],needles=needles,hits=hits))
    assert not any(r['hits'] for r in rows)
    return dict(schema='tno.external_effects.twilight_whole_compat.v1',baseline=BASELINE,status='STATIC_ATTRIBUTION_COMPLETE',scope='Exact outer Twilight forward namespace scan and four pinned candidate reverse scans; gzip resources decoded. Registered nested31 transformer behavior separately reviewed. This does not assert absence of generic or dynamically composed effects in the entire installed pack.',scans=rows,direct_tensura_l2_source_specific='NONE_PROVEN',generic_attribution='GENERIC_CONDITIONAL_PRESENT',native_optional_integrations=['Protected Curios actual capability/slot consumption and retention','Protected Parry loaded-mod suppression of Twilight parry callback','CosmeticArmorReworked conditional inventory-only preservation; excluded combat package'],generic_hook_reference=dict(file='compat-findings/twilightforest-frosted.json',sha256=sha256(OUT/'compat-findings/twilightforest-frosted.json')),native_integration_reference=dict(file='semantic-sections/twilightforest-combat-closure.json',sha256=sha256(OUT/'semantic-sections/twilightforest-combat-closure.json')),unknown='Other runtime listeners, configs, tag reloads and actual Tensura/L2/Stage results remain future approved runtime work, not unresolved native semantics.',**boundary_flags())


def collect():
    target=next(t for t in read_json(OUT/'jar-inventory.json')['targets'] if t['key']=='twilightforest')
    native(BATCH,{c:list(ms) for c,ms in EXCLUDED.items()})
    write_json(OUT/'compat-findings/twilightforest-global.json',compat_census())
    api=api_census(target);assert api['class_count']==1943 and api['method_hit_count']==279
    write_json(OUT/'twilightforest-global-source-census.json',api)
    sections=[]
    for p in sorted((OUT/'semantic-sections').glob('twilightforest-*.json')):
        s=read_json(p);sections.append(dict(file=p.relative_to(OUT).as_posix(),sha256=sha256(p),checkpoint=s.get('checkpoint'),counts=s.get('counts'),scope='Protected reviewed subset. Final filtering/deduplication does not rewrite this source.'))
    damage=damage_census();assert damage['declared']==damage['used']==40 and not damage['unfinished_types']
    write_json(OUT/'twilightforest-global-source-closure.json',dict(schema='tno.external_effects.twilight_global_closure.v1',baseline=BASELINE,checkpoint='R2f8-remaining-content-complete',decision='TWILIGHT_REMAINING_CONTENT_COMPLETE',status='SEMANTIC_DISCOVERY_COMPLETE_PENDING_DEDUP_PROMOTION',source_sha=git('rev-parse','HEAD').strip(),semantic_discovery_complete=True,special_damage_discovery_complete=True,source_mapping_complete=True,delivery_mapping_complete=True,combat_asm_coverage_complete=True,compatibility_attribution_complete=True,final_promotion_complete=False,reviewed_draft_mechanics=277,reviewed_draft_paths=1014,final_distinct_mechanic_count=None,final_distinct_delivery_count=None,custom_damage_types=40,custom_status_effects=['twilightforest:frosted'],review_required=[],remaining_native_ambiguities=[],unfinished_combat_significant_work=[],runtime_tests=0,sections=sections,source_census=dict(file='twilightforest-global-source-census.json',sha256=sha256(OUT/'twilightforest-global-source-census.json')),compatibility=dict(file='compat-findings/twilightforest-global.json',sha256=sha256(OUT/'compat-findings/twilightforest-global.json')),damage_type_closure=dict(file='twilightforest-r2f8y-damage-type-closure.json',sha256=sha256(OUT/'twilightforest-r2f8y-damage-type-closure.json')),corrected_scope='Combat damage/status/control/healing/resources/defense/admission/attributes and materially distinct native delivery. No new deep utility/progression/acquisition/GUI/cosmetic/noncombat-worldgen subsections.',exclusions=EXCLUDED,semantic_exclusions='Reuses protected full-class exclusions: ordinary HelmetCrab primitives, unregistered Boggard, non-attacking Harbinger/Roving/Plateau placeholders, ordinary prey targeting, enderman terrain-grief wrapper, loot/advancement consumers and noncombat utility/rendering. Historical utility draft packages are filtered at final promotion with an explicit total mapping.',exact_next_task='Immediately deduplicate all277 mechanic drafts/1014 path cases, retain material native delivery differences, promote Twilight COMPLETE in five views/ledger, validate and push/live verify. Only then begin narrow IceAndFireCE beta15.',**boundary_flags()))


if __name__=='__main__':collect()
