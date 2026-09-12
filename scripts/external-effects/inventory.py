"""Pin exact installed artifacts and create the R1 research scaffold once."""
import json
import tomllib
import zipfile
from catalog_common import *

def inspect(path, key, role):
    if not path.is_file():
        return dict(key=key, filename=path.name, path=str(path), status='UNAVAILABLE', role=role)
    with zipfile.ZipFile(path) as jar:
        names = jar.namelist()
        metadata = []
        for name in ('META-INF/neoforge.mods.toml','META-INF/mods.toml','fabric.mod.json','META-INF/MANIFEST.MF'):
            if name in names:
                text = archive_text(jar, name)
                parsed = tomllib.loads(text) if name.endswith('.toml') else json.loads(text) if name.endswith('.json') else text
                metadata.append(dict(entry=name, sha256=byte_hash(jar.read(name)), parsed=parsed))
        classes = [n for n in names if n.endswith('.class')]
        return dict(key=key, filename=path.name, path=str(path), status='AVAILABLE_EXACT_FILENAME',
            role=role, size_bytes=path.stat().st_size, sha256=sha256(path), entries=len(names),
            classes=len(classes), metadata=metadata,
            classfile_major_versions=sorted({int.from_bytes(jar.read(n)[6:8], 'big') for n in classes}),
            damage_type_resources=[n for n in names if '/damage_type/' in n and '/tags/' not in n and n.endswith('.json')],
            damage_tag_resources=[n for n in names if '/tags/damage_type/' in n and n.endswith('.json')],
            mixin_configs=[n for n in names if 'mixin' in n.lower() and n.endswith('.json')],
            discovery_status='REFERENCE_ONLY' if role=='BASE_TENSURA_REFERENCE' else 'NOT_STARTED')

def main():
    assert git('rev-parse', 'HEAD') == BASELINE, 'R1 must start from verified baseline'
    assert not (OUT/'jar-inventory.json').exists(), 'Preserve existing inventory; do not regenerate on resume'
    targets = [inspect(MODS/name, key, 'BASE_TENSURA_REFERENCE' if key=='tensura' else 'EXTERNAL_TARGET') for key,name in TARGETS]
    compat = [inspect(path, path.stem, 'EXISTING_COMPAT_CANDIDATE') for path in sorted(MODS.glob('*.jar'))
              if 'compat' in path.name.lower() or path.name.startswith('tensura_iaf-')]
    vanilla = []
    for name in ('neoforge-21.1.248.jar','neoforge-21.1.248-sources.jar','neoforge-21.1.248-client-extra-aka-minecraft-resources.jar'):
        path=ROOT/'build/moddev/artifacts'/name
        vanilla.append(dict(path=str(path), sha256=sha256(path), role='LOCAL_MAPPED_MINECRAFT_1_21_1_WITH_NEOFORGE_PATCHES',
            note='Compare relevant methods against raw vanilla/mappings as needed; do not label a NeoForge patch as vanilla behavior.'))
    inventory=dict(schema='tno.external_effects.jar_inventory.v1', checkpoint='R1', status='COMPLETE',
        baseline=BASELINE, source_directory=str(MODS), source_directory_confirmed_by_owner=True,
        exact_filename_policy='No version substitutions; byte hashes identify the selected installed artifacts.',
        inspected_inventory_count=sum(t['status']=='AVAILABLE_EXACT_FILENAME' for t in targets),
        unavailable_count=sum(t['status']=='UNAVAILABLE' for t in targets), targets=targets,
        compat_candidates=compat, compat_discovery_limit='Filename candidates only at R1; package/mixin/callback review remains in R2. Presence is not proof of a behavioral modification.',
        vanilla_reference_artifacts=vanilla, **boundary_flags())
    write_json(OUT/'jar-inventory.json', inventory)
    references=[]
    for family,doc in [('MAGIC','phase-6-endgame-magic-holy-production.md'),('HOLY','phase-6-endgame-magic-holy-production.md'),
        ('SOUL','phase-6-soul-native-event-path-research.md'),('ELEMENTAL','phase-6-elemental-native-event-path-research.md'),
        ('ENERGY_STEAL','phase-6-energy-steal-physical-prerequisite-research.md'),('SEVERANCE','phase-6-severance-regenerate-research.md')]:
        path='docs/'+doc
        references.append(dict(family=family,coverage='TENSURA_NATIVE_EXISTING_TNO_COVERAGE',
            revision=BASELINE, path=path, git_blob=git('rev-parse',BASELINE+':'+path), repeat_research=False))
    shared=dict(status='PARTIAL', checkpoint='R1', baseline=BASELINE,
        note='Empty arrays mean discovery not performed yet, never no effects. R2 discovery, R3 comparison and R4 acceptance remain pending.')
    for filename, schema, data in [
        ('effect-catalog.json','catalog',dict(effects=[],existing_tno_coverage=references)),
        ('effect-sources.json','sources',dict(sources=[])),
        ('delivery-path-matrix.json','delivery',dict(paths=[])),
        ('vanilla-comparison.json','vanilla_comparison',dict(comparisons=[])),
        ('behavior-primitives.json','primitives',dict(primitives=[]))]:
        write_json(OUT/filename,dict(schema='tno.external_effects.'+schema+'.v1',**shared,**data))
    write_json(OUT/'research-decision.json',dict(schema='tno.external_effects.decision.v1',
        status='PARTIAL', checkpoint='R1', decision='EXTERNAL_EFFECT_CATALOG_IN_PROGRESS',
        baseline=BASELINE, branch='external-effects-catalog-research',
        checkpoints=dict(R1='Commit containing initial inventory/scaffold; verify SHA after push',R2=None,R3=None,R4=None),
        effect_coverage_complete=False, delivery_coverage_complete=False,
        next_task='R2: broad static discovery across all exact external JARs, including non-MobEffect paths and existing compat modifications. Base Tensura is reference-only.',
        stop_after_R4=True, **boundary_flags()))
    print(f'R1 inventory: {inventory["inspected_inventory_count"]}/23 exact JARs available; {len(compat)} compat candidates.')

if __name__=='__main__': main()
