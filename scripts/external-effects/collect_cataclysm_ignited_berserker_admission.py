"""Capture only R2k13a Ignited Berserker admission/state/spawn witnesses.

Reuse Internal_Animation_Monster and Animation_Monsters metadata/contracts,
patched native admission, attribute binding and Ignis world-state evidence.
Never recapture offense, visual state methods or protected parent bodies.
"""
import argparse
import hashlib
from pathlib import Path
import zipfile

from catalog_common import BASELINE, OUT, read_json, write_json
from classfile import ClassFile, Reader
from collect_cataclysm_ender_golem_offense import instructions

PKG = 'com/github/L_Ender/cataclysm/'
B = 'entity/InternalAnimationMonster/Ignited_Berserker_Entity'
REGISTRY = 'init/ModEntities'
SPEC_FILE = OUT / 'native-specifications/cataclysm-ignited-berserker-admission.json'
EVIDENCE_FILE = OUT / 'native-evidence/cataclysm-ignited-berserker-admission.json'
METHODS = {
    B: ['ignited_berserker', 'decreaseAirSupply', 'defineSynchedData',
        'canBePushedByEntity', 'canRide', 'die', 'deathtimer', 'checkSpawnRules',
        'addAdditionalSaveData', 'readAdditionalSaveData'],
    REGISTRY: ['lambda$static$23', 'rollSpawn'],
}
FRAGMENTS = {
    B: {'<init>': [[0, 3], [83, 90], [99, 116]]},
    REGISTRY: {'<clinit>': [[403, 417]], 'registerSpawnPlacements': [[243, 267]]},
}


def specification():
    return dict(schema='tno.external_effects.native_specification.v1', baseline=BASELINE,
        evidence_specifications=[dict(id='cataclysm:ignited-berserker-admission:' + n,
            mod_key='cataclysm', entry=PKG + n + '.class', methods=methods,
            method_fragments=FRAGMENTS.get(n, {})) for n, methods in sorted(METHODS.items())])


def collect(jar_path):
    target = next(t for t in read_json(OUT / 'jar-inventory.json')['targets'] if t['key']=='cataclysm')
    jar_path = Path(jar_path)
    with jar_path.open('rb') as stream:
        assert hashlib.file_digest(stream, 'sha256').hexdigest()==target['sha256']
    assert jar_path.stat().st_size==target['size_bytes']
    witnesses = []
    with zipfile.ZipFile(jar_path) as jar:
        for spec in specification()['evidence_specifications']:
            raw = jar.read(spec['entry'])
            c = ClassFile(raw)
            row = dict(id=spec['id'], mod_key='cataclysm', jar_sha256=target['sha256'],
                entry=spec['entry'], entry_sha256=hashlib.sha256(raw).hexdigest(),
                class_name=c.name, superclass=c.super, interfaces=c.interfaces, methods=[])
            if spec['entry']==PKG+B+'.class':
                row['declared_method_names'] = sorted({m['name'] for m in c.methods})
                row['declared_fields'] = [dict(name=f['name'],descriptor=f['descriptor']) for f in c.fields]
                ctor = next(m for m in c.methods if m['name']=='<init>')
                row['constructor_nonvisual_invocations'] = [i['operand']
                    for i in instructions(c,ctor['code']) if i['opcode'] in {'0xb6','0xb7','0xb8','0xb9'}
                    and not str(i['operand']).startswith('net/minecraft/world/entity/AnimationState.')]
            for name in spec['methods'] + list(spec['method_fragments']):
                matches = [m for m in c.methods if m['name']==name]
                assert matches, (spec['entry'],name)
                for m in matches:
                    code = m.get('code',b'')
                    ins = instructions(c,code)
                    ranges = spec['method_fragments'].get(name)
                    if ranges:
                        ins = [i for i in ins if any(a<=i['offset']<=b for a,b in ranges)]
                        assert all(any(i['offset']==v for i in ins) for span in ranges for v in span)
                    row['methods'].append(dict(name=name,descriptor=m['descriptor'],
                        code_sha256=hashlib.sha256(code).hexdigest(),instructions=ins,
                        **({'instruction_offset_ranges':ranges} if ranges else {})))
            if spec['entry']==PKG+REGISTRY+'.class':
                r = Reader(next(data for name,data in c.attributes if name=='BootstrapMethods'))
                bs = [(r.u2(),[r.u2() for _ in range(r.u2())]) for _ in range(r.u2())]
                indices = sorted({int(i['operand'].split('#')[1].split(':')[0])
                    for m in row['methods'] for i in m['instructions'] if i['opcode']=='0xba'})
                row['registration_bootstraps'] = [dict(index=i,handle=c.resolve(bs[i][0]),
                    arguments=[c.resolve(a) for a in bs[i][1]]) for i in indices]
            witnesses.append(row)
    return dict(schema='tno.external_effects.native_evidence.v1',baseline=BASELINE,
        status='STATIC_EVIDENCE',witnesses=witnesses,
        note='Two exact entries only: Berserker construction/attributes, environment, '
             'parent-only NBT, raw death-state reset, instance spawn prerequisite; '
             'its exact factory/ID/placement binding and called rollSpawn helper. '
             'No tick/aiStep/goals/AreaAttack/AreaSwordAttack/payloads or animation-only '
             'method bodies. Locked parent/native/world-state/attribute evidence reused; '
             'no boss-contract recapture, recursive scan, runtime or Stage decisions.')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('jar',type=Path,help='Exact pinned Cataclysm 3.27 JAR')
    evidence=collect(parser.parse_args().jar)
    write_json(SPEC_FILE,specification())
    write_json(EVIDENCE_FILE,evidence)
    print(f'Ignited Berserker admission: {len(evidence["witnesses"])} scoped witnesses captured')
