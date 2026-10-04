"""Bounded R2k12a Ignited Revenant admission/state/encounter witnesses.

Read five exact entries from the pinned JAR. Offensive tick/goal execution and
payload classes are excluded; shared admission, goal and native shield contracts
are reused without recapture.
"""
import argparse
import hashlib
from pathlib import Path
import zipfile

from catalog_common import BASELINE, OUT, read_json, write_json
from classfile import ClassFile, Reader
from collect_cataclysm_ender_golem_offense import instructions

PKG = 'com/github/L_Ender/cataclysm/'
R = 'entity/AnimationMonster/BossMonsters/Ignited_Revenant_Entity'
REGISTRY = 'init/ModEntities'
PIECE = 'structures/Burning_Arena_Structure$Piece'
SPEC_FILE = OUT / 'native-specifications/cataclysm-ignited-revenant-admission.json'
EVIDENCE_FILE = OUT / 'native-evidence/cataclysm-ignited-revenant-admission.json'
METHODS = {
    R: ['hurt', 'getApproximateAttackDamageWithItem', 'canBlockDamageSource',
        'defineSynchedData', 'setIsAnger', 'getIsAnger', 'setShieldDurability',
        'getShieldDurability', 'addAdditionalSaveData', 'readAdditionalSaveData',
        'ignited_revenant', 'decreaseAirSupply', 'canBePushedByEntity'],
    R + '$Ignited_Revenant_Goal': ['<init>', 'start', 'stop'],
    R + '$ShootGoal': ['<init>', 'start', 'stop'],
    REGISTRY: ['lambda$static$22'],
    PIECE: ['handleDataMarker'],
}
FRAGMENTS = {
    R: {'<init>': [[0, 19], [28, 56]], 'tick': [[0, 103]],
        'registerGoals': [[0, 13], [36, 53], [94, 133]]},
    REGISTRY: {'<clinit>': [[386, 400]]},
}


def specification():
    return dict(schema='tno.external_effects.native_specification.v1', baseline=BASELINE,
        evidence_specifications=[dict(id='cataclysm:ignited-revenant-admission:' + n,
            mod_key='cataclysm', entry=PKG + n + '.class', methods=methods,
            method_fragments=FRAGMENTS.get(n, {})) for n, methods in sorted(METHODS.items())])


def collect(jar_path):
    target = next(t for t in read_json(OUT / 'jar-inventory.json')['targets']
                  if t['key'] == 'cataclysm')
    jar_path = Path(jar_path)
    with jar_path.open('rb') as stream:
        assert hashlib.file_digest(stream, 'sha256').hexdigest() == target['sha256']
    assert jar_path.stat().st_size == target['size_bytes']
    witnesses = []
    with zipfile.ZipFile(jar_path) as jar:
        for spec in specification()['evidence_specifications']:
            raw = jar.read(spec['entry'])
            c = ClassFile(raw)
            row = dict(id=spec['id'], mod_key='cataclysm', jar_sha256=target['sha256'],
                entry=spec['entry'], entry_sha256=hashlib.sha256(raw).hexdigest(),
                class_name=c.name, superclass=c.super, interfaces=c.interfaces, methods=[])
            if spec['entry'] == PKG + R + '.class':
                row['declared_method_names'] = sorted({m['name'] for m in c.methods})
                row['declared_fields'] = [dict(name=f['name'], descriptor=f['descriptor']) for f in c.fields]
            for name in spec['methods'] + list(spec['method_fragments']):
                matches = [m for m in c.methods if m['name'] == name]
                assert matches, (spec['entry'], name)
                for m in matches:
                    code = m.get('code', b'')
                    ins = instructions(c, code)
                    ranges = spec['method_fragments'].get(name)
                    if ranges:
                        ins = [i for i in ins if any(a <= i['offset'] <= b for a, b in ranges)]
                        assert all(any(i['offset'] == v for i in ins) for span in ranges for v in span)
                    row['methods'].append(dict(name=name, descriptor=m['descriptor'],
                        code_sha256=hashlib.sha256(code).hexdigest(), instructions=ins,
                        **({'instruction_offset_ranges': ranges} if ranges else {})))
            if spec['entry'] == PKG + REGISTRY + '.class':
                r = Reader(next(data for name, data in c.attributes if name == 'BootstrapMethods'))
                bs = [(r.u2(), [r.u2() for _ in range(r.u2())]) for _ in range(r.u2())]
                indices = sorted({int(i['operand'].split('#')[1].split(':')[0])
                    for m in row['methods'] for i in m['instructions'] if i['opcode'] == '0xba'})
                row['registration_bootstraps'] = [dict(index=i, handle=c.resolve(bs[i][0]),
                    arguments=[c.resolve(a) for a in bs[i][1]]) for i in indices]
            witnesses.append(row)
    return dict(schema='tno.external_effects.native_evidence.v1', baseline=BASELINE,
        status='STATIC_EVIDENCE', witnesses=witnesses,
        note='Concrete axe/shield admission and source predicates, raw anger/shield '
             'state and start/stop writers, parent-only NBT, construction/attributes, '
             'environment/fall motion and exact Burning Arena revenant marker only. '
             'No offensive tick regions, attack selection/timing, goal execution or '
             'payload classes. Existing LLibrary/shared/status/goal/native shield and '
             'attribute registration evidence reused; no recursive scan or runtime.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('jar', type=Path, help='Exact pinned Cataclysm 3.27 JAR')
    evidence = collect(parser.parse_args().jar)
    write_json(SPEC_FILE, specification())
    write_json(EVIDENCE_FILE, evidence)
    print(f'Ignited Revenant admission: {len(evidence["witnesses"])} scoped witnesses captured')
