"""Preserve already reviewed R2b facts and exact resume state before usage exhaustion."""
from catalog_common import *
from native_evidence import collect
from vanilla_reference import prepare
from assemble_native import assemble

if __name__=='__main__':
    path=OUT/'native-findings'/'variantsandventures.json'; document=read_json(path)
    specs=document['evidence_specifications']
    main=next(x for x in specs if x['id']=='vv-main')
    if 'initEvents' not in main['methods']:main['methods'].append('initEvents')
    for name in ['ZombieMobMixin','ZombiePathfinderMobMixin','ZombieMonsterMixin']:
        spec=dict(id='vv-chain-'+name,mod_key='variantsandventures',entry='com/faboslav/variantsandventures/common/mixin/'+name+'.class',methods=[])
        if spec['id'] not in {x['id'] for x in specs}:specs.append(spec)
    for name in ['zombies','skeletons','freeze_immune_entity_types','powder_snow_walkable_mobs','can_breathe_under_water']:
        spec=dict(id='vv-tag-'+name,mod_key='variantsandventures',entry='data/minecraft/tags/entity_type/'+name+'.json')
        if spec['id'] not in {x['id'] for x in specs}:specs.append(spec)
    document['native_prerequisite_followup']='docs/benchmarks/external-effects-catalog/native-prerequisites/variantsandventures.json'
    document['exact_resume']='Resume from R2b raw-vanilla prerequisite findings; final source/delivery coverage, candidate exclusions and classifications remain unfinished. Do not repeat the saved poison-duration/freeze/arrow-inertia tracing.'
    write_json(path,document)
    write_json(OUT/'native-evidence'/'variantsandventures.json',collect(document))
    notes=read_json(OUT/'partial-notes'/'cultofazazel.json')
    write_json(OUT/'native-evidence'/'cultofazazel-partial.json',collect(notes))
    spec=read_json(OUT/'vanilla-specifications'/'variants-prerequisites.json')
    write_json(OUT/'vanilla-evidence'/'variants-prerequisites.json',prepare(spec))
    manifest=MODS.parent/'manifest.json';instance=read_json(manifest)
    loader_root=Path('C:/Users/youra/curseforge/minecraft/Install/libraries/net/neoforged/neoforge/21.1.244')
    write_json(OUT/'instance-loader-reference.json',dict(schema='tno.external_effects.loader_reference.v1',
        baseline=BASELINE,status='IDENTITY_ONLY',manifest_path=str(manifest),manifest_sha256=sha256(manifest),
        minecraft=instance['minecraft'],
        artifacts=[dict(path=str(loader_root/name),sha256=sha256(loader_root/name),semantic_review='NOT_STARTED')
                   for name in ('neoforge-21.1.244-client.jar','neoforge-21.1.244-universal.jar')],
        note='The installed manifest declares 21.1.244. Development mapped source aids use 21.1.248 and must not be represented as exact installed-loader behavior.'))
    catalog=read_json(OUT/'effect-catalog.json');catalog.update(checkpoint='R2b_PARTIAL',effects=assemble())
    write_json(OUT/'effect-catalog.json',catalog)
    decision=read_json(OUT/'research-decision.json')
    decision.update(checkpoint='R2b_PARTIAL',save_mode=True,
        save_reason='Account usage check reported 80 percent of the current five-hour window consumed. Owner save-mode instruction applied; new research stopped before preserving and validating R2b.',
        next_task='Resume R2 from protected R2b. Read native-prerequisites/variantsandventures.json and partial-notes/cultofazazel.json. Finish Variants & Ventures source/delivery/exclusion coverage, conversion and exact-loader 21.1.244 distinctions; continue Cult of Azazel at registry IDs, Curios helper and ZoneEffect consumers. Then continue remaining external targets, nested archives, resource/decompiler anomalies and compat attribution. R2/R3/R4 remain incomplete; do not restart R1/R2a or repeat Phase 6. No boss/L2/Stage work.')
    decision['checkpoints']['R2a']='2e9d999ca68c101ac26c9e41415a696db7c5f65b'
    decision['checkpoints']['R2b']='Self: commit containing validated R2b save-mode evidence; resolve with git log and verify live remote SHA.'
    write_json(OUT/'research-decision.json',decision)
    print('Saved R2b: 22 Variants & Ventures witnesses, 5 Cult of Azazel partial witnesses, raw vanilla prerequisite evidence; all coverage decisions remain partial.')
