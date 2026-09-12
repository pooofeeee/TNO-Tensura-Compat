"""Save the inspected data-only compat contribution separately from Antarchy native mechanics."""
from catalog_common import *

if __name__=='__main__':
    inv=read_json(OUT/'jar-inventory.json')
    compat=next(t for t in inv['compat_candidates'] if t['key']=='antarchy_tensura_compat-1.0.0')
    native=next(t for t in inv['targets'] if t['key']=='antarchy')
    entries=[]
    with zipfile.ZipFile(compat['path']) as jar,zipfile.ZipFile(native['path']) as source:
        classes=[name for name in jar.namelist() if name.endswith('.class')]
        for name in sorted(jar.namelist()):
            if name.startswith('data/tensura/entity_existence/') and name.endswith('.json'):
                data=jar.read(name)
                entries.append(dict(entry=name,sha256=byte_hash(data),data=json.loads(data),same_path_in_native_jar=name in source.namelist()))
    report=dict(schema='tno.external_effects.compat_findings.v1',baseline=BASELINE,status='PARTIAL',
        mod_key=compat['key'],native_mod_key='antarchy',compat_jar_sha256=compat['sha256'],native_jar_sha256=native['sha256'],
        existing_compat_modification='PRESENT',
        exact_proven_change='Data-only JAR contributes Tensura entity_existence definitions for Antarchy entities: spiritualHealth, magicule ranges, optional aura ranges and optional base Tensura ability IDs. These are compatibility-layer declarations, not Antarchy-native mechanics or new addon skill implementations.',
        java_classes=len(classes),definitions=len(entries),entries=entries,
        pending=['Verify exact base Tensura data loader interpretation and resource conflict precedence against other installed data. Do not infer effective runtime SHP or skill activation from declarations alone.',
                 'Antarchy native effect/damage implementation review remains pending and is separate.'],
        runtime_tested=False,semantic_coverage_complete=False)
    write_json(OUT/'compat-findings'/'antarchy-tensura-data.json',report)
    print(json.dumps({k:v for k,v in report.items() if k!='entries'},indent=2))
