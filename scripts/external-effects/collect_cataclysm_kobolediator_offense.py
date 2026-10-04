"""Capture only new R2k14b Kobolediator offense/goal witnesses.

Reuse admission, shared goals/state/queries, native source/shield and the
already-proven non-damaging falling-block debris lifecycle without recapture.
"""
import argparse
import hashlib
from pathlib import Path
import zipfile

from catalog_common import BASELINE, OUT, read_json, write_json
from classfile import ClassFile
from collect_cataclysm_ignited_revenant_offense import instructions

PKG = 'com/github/L_Ender/cataclysm/'
K = 'entity/InternalAnimationMonster/Kobolediator_Entity'
SPEC_FILE = OUT / 'native-specifications/cataclysm-kobolediator-offense.json'
EVIDENCE_FILE = OUT / 'native-evidence/cataclysm-kobolediator-offense.json'
METHODS = {
    K: ['AreaAttack','StompDamage','spawnBlocks','ChargeBlockBreaking','isAlliedTo'],
    K+'$1': ['<init>','canUse','stop'],
    K+'$2': ['<init>','canUse'],
    K+'$3': ['<init>','tick'],
    K+'$4': ['<init>','stop'],
    K+'$5': ['<init>','stop'],
}
FRAGMENTS = {K: {
    'tick': [[0,1],[54,88]],
    'registerGoals': [[57,269]],
    'aiStep': [[0,1],[40,70],[105,147],[160,202],[215,258],[271,315],
               [328,372],[385,414],[451,472],[509,533],[583,850],[887,887]],
}}


def specification():
    return dict(schema='tno.external_effects.native_specification.v1',baseline=BASELINE,
        evidence_specifications=[dict(id='cataclysm:kobolediator-offense:'+n,mod_key='cataclysm',
            entry=PKG+n+'.class',methods=methods,method_fragments=FRAGMENTS.get(n,{}))
            for n,methods in sorted(METHODS.items())])


def collect(jar_path):
    target=next(t for t in read_json(OUT/'jar-inventory.json')['targets'] if t['key']=='cataclysm')
    jar_path=Path(jar_path)
    with jar_path.open('rb') as stream:
        assert hashlib.file_digest(stream,'sha256').hexdigest()==target['sha256']
    assert jar_path.stat().st_size==target['size_bytes']
    witnesses=[]
    with zipfile.ZipFile(jar_path) as jar:
        for spec in specification()['evidence_specifications']:
            raw=jar.read(spec['entry']);c=ClassFile(raw)
            row=dict(id=spec['id'],mod_key='cataclysm',jar_sha256=target['sha256'],entry=spec['entry'],
                entry_sha256=hashlib.sha256(raw).hexdigest(),class_name=c.name,superclass=c.super,
                interfaces=c.interfaces,methods=[])
            row['declared_method_names']=sorted({m['name'] for m in c.methods})
            for name in spec['methods']+list(spec['method_fragments']):
                matches=[m for m in c.methods if m['name']==name]
                assert matches,(spec['entry'],name)
                for m in matches:
                    code=m.get('code',b'');ins=instructions(c,code);ranges=spec['method_fragments'].get(name)
                    if ranges:
                        ins=[i for i in ins if any(a<=i['offset']<=b for a,b in ranges)]
                        assert all(any(i['offset']==v for i in ins) for span in ranges for v in span)
                    row['methods'].append(dict(name=name,descriptor=m['descriptor'],code_sha256=hashlib.sha256(code).hexdigest(),
                        instructions=ins,**({'instruction_offset_ranges':ranges} if ranges else {})))
            witnesses.append(row)
    return dict(schema='tno.external_effects.native_evidence.v1',baseline=BASELINE,status='STATIC_EVIDENCE',witnesses=witnesses,
        note='Six exact entries: Kobolediator offense fragments, direct area/stomp/sample/terrain/alliance helpers '
             'and its five directly registered offensive goals. Utility and presentation/sound/shake/particle instructions excluded. '
             'Protected incoming/state/NBT/construction/encounter, shared goal/source/shield/query contracts and '
             'Cm_Falling_Block_Entity lifecycle reused without regeneration. Debris damage remains separate from '
             'boss-owned sample damage. No recursive JAR scan, runtime or Stage policy.')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('jar',type=Path,help='Exact pinned Cataclysm 3.27 JAR')
    evidence=collect(parser.parse_args().jar)
    write_json(SPEC_FILE,specification());write_json(EVIDENCE_FILE,evidence)
    print(f'Kobolediator offense: {len(evidence["witnesses"])} scoped witnesses captured')
