"""Bounded R2k11a Ender Golem admission/state/encounter witnesses.

Read three exact entries from the pinned JAR. Existing shared/native contracts
and attribute registration are reused; all offensive execution is deferred.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import zipfile

from catalog_common import BASELINE, OUT, read_json, write_json
from classfile import ClassFile, Reader

PKG = 'com/github/L_Ender/cataclysm/'
G = 'entity/AnimationMonster/BossMonsters/Ender_Golem_Entity'
REGISTRY = 'init/ModEntities'
PIECE = 'structures/RuinedCitadelStructure$Piece'
SPEC_FILE = OUT / 'native-specifications/cataclysm-ender-golem-admission.json'
EVIDENCE_FILE = OUT / 'native-evidence/cataclysm-ender-golem-admission.json'
METHODS = {
    G: ['hurt', 'RangeLimit', 'ender_golem', 'decreaseAirSupply',
        'defineSynchedData', 'setIsAwaken', 'getIsAwaken',
        'addAdditionalSaveData', 'readAdditionalSaveData', 'canBePushedByEntity'],
    REGISTRY: ['lambda$static$0'],
    PIECE: [],
}
FRAGMENTS = {
    G: {'<init>': [[0, 8], [25, 45]],
        'tick': [[0, 1], [20, 122], [584, 656]],
        'registerGoals': [[87, 145]]},
    REGISTRY: {'<clinit>': [[12, 26]]},
    PIECE: {'handleDataMarker': [[0, 13], [184, 250]]},
}


def specification():
    return dict(schema='tno.external_effects.native_specification.v1', baseline=BASELINE,
        evidence_specifications=[dict(id='cataclysm:ender-golem-admission:' + n,
            mod_key='cataclysm', entry=PKG + n + '.class', methods=methods,
            method_fragments=FRAGMENTS[n]) for n, methods in sorted(METHODS.items())])


def instructions(c, code):
    """Keep branch destinations for the concrete Boolean/source admission proof."""
    result = list(c.instructions(code))
    for i in result:
        if 0x99 <= int(i['opcode'], 16) <= 0xa8 or i['opcode'] in {'0xc6', '0xc7'}:
            i['branch_target'] = i['offset'] + struct.unpack_from('>h', code, i['offset'] + 1)[0]
    return result


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
            if spec['entry'] == PKG + G + '.class':
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
        note='Ender Golem concrete incoming reductions/order, concrete range and absent '
             'cap/DPS/regen/invulnerability overrides, awake/target/deactivation state, '
             'dormant native heal, combat NBT, attributes/constructor, type factory and '
             'Ruined Citadel golem marker prerequisites only. Tick includes state/heal '
             'fragments only; target registrations exclude offensive goals. Existing '
             'shared/status/attribute registration evidence reused. No offensive payload '
             'research, whole-JAR scan, runtime or Stage policy decision.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('jar', type=Path, help='Exact pinned Cataclysm 3.27 JAR')
    evidence = collect(parser.parse_args().jar)
    write_json(SPEC_FILE, specification())
    write_json(EVIDENCE_FILE, evidence)
    print(f'Ender Golem admission: {len(evidence["witnesses"])} scoped witnesses captured')
