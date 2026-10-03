"""Missing R2k7a Ancient Remnant admission/setup witnesses from the pinned JAR.

Only exact class entries and scoped fragments. Locked shared/status and prior
boss contracts are reused; Ancient Remnant offense/payloads remain deferred.
"""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

from catalog_common import BASELINE, OUT, read_json, write_json
from classfile import ClassFile, Reader

PKG = 'com/github/L_Ender/cataclysm/'
R = 'entity/InternalAnimationMonster/IABossMonsters/Ancient_Remnant/Ancient_Remnant_Entity'
BASE = 'entity/InternalAnimationMonster/IABossMonsters/IABoss_monster'
IA = 'entity/InternalAnimationMonster/Internal_Animation_Monster'
AM = 'entity/etc/Animation_Monsters'
PIECE = 'structures/Cursed_Pyramid_Structure$Piece'
REGISTRY = 'init/ModEntities'
SPEC_FILE = OUT / 'native-specifications/cataclysm-remnant-admission.json'
EVIDENCE_FILE = OUT / 'native-evidence/cataclysm-remnant-admission.json'
METHODS = {
    R: ['<init>', 'hurt', 'DamageCap', 'DpsCap', 'RangeLimit', 'NatureRegen',
        'defineSynchedData', 'isSleep', 'setNecklace', 'getNecklace',
        'setRage', 'getRage', 'setIsPower', 'getIsPower', 'isPower',
        'setCrash', 'getCrash', 'addAdditionalSaveData', 'readAdditionalSaveData',
        'mobInteract', 'canBeSeenAsEnemy', 'finalizeSpawn', 'maledictus'],
    R + '$RemnantDoNothingGoal': ['<init>', 'canUse', 'tick', 'isInterruptable',
                                'requiresUpdateEveryTick'],
    R + '$RemnantAwakenGoal': ['<init>', 'canUse'],
    R + '$RemnantPhaseChangeGoal': ['<init>', 'canUse'],
    # Only declaration metadata establishes absence/inheritance. No recaptured bodies.
    BASE: [], IA: [], AM: [], PIECE: [],
    REGISTRY: ['lambda$static$78'],
}
FRAGMENTS = {
    R: {'registerGoals': [[189, 248]],
        'tick': [[0, 1], [236, 255]],
        'aiStep': [[0, 1], [494, 509], [560, 562]]},
    # String switch's remnant label and ONLY its native spawn branch.
    PIECE: {'handleDataMarker': [[148, 163], [556, 651]]},
    # The attribute binding already exists in locked Guardian evidence.
    REGISTRY: {'<clinit>': [[1338, 1352]]},
}


def specification():
    rows = [dict(id='cataclysm:remnant-admission:' + n, mod_key='cataclysm',
        entry=PKG + n + '.class', methods=methods,
        **({'method_fragments': FRAGMENTS[n]} if n in FRAGMENTS else {}))
        for n, methods in sorted(METHODS.items())]
    return dict(schema='tno.external_effects.native_specification.v1', baseline=BASELINE,
                evidence_specifications=rows)


def collect(jar_path):
    target = next(t for t in read_json(OUT / 'jar-inventory.json')['targets'] if t['key'] == 'cataclysm')
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
            if spec['entry'] in [PKG + n + '.class' for n in [R, BASE, IA, AM]]:
                row['declared_method_names'] = sorted({m['name'] for m in c.methods})
                row['declared_fields'] = [dict(name=f['name'], descriptor=f['descriptor']) for f in c.fields]
            for name in spec['methods'] + list(spec.get('method_fragments', {})):
                matches = [m for m in c.methods if m['name'] == name]
                assert matches, (spec['entry'], name)
                for m in matches:
                    code = m.get('code', b'')
                    ins = list(c.instructions(code))
                    ranges = spec.get('method_fragments', {}).get(name)
                    if ranges:
                        ins = [i for i in ins if any(a <= i['offset'] <= b for a, b in ranges)]
                        assert all(any(i['offset'] == v for i in ins) for r in ranges for v in r), (spec['entry'], name, ranges)
                    row['methods'].append(dict(name=name, descriptor=m['descriptor'],
                        code_sha256=hashlib.sha256(code).hexdigest(), instructions=ins,
                        **({'instruction_offset_ranges': ranges} if ranges else {})))
            if spec['entry'] == PKG + REGISTRY + '.class':
                r = Reader(next(data for n, data in c.attributes if n == 'BootstrapMethods'))
                bs = [(r.u2(), [r.u2() for _ in range(r.u2())]) for _ in range(r.u2())]
                indices = sorted({int(i['operand'].split('#')[1].split(':')[0])
                    for m in row['methods'] for i in m['instructions'] if i['opcode'] == '0xba'})
                row['registration_bootstraps'] = [dict(index=i, handle=c.resolve(bs[i][0]),
                    arguments=[c.resolve(a) for a in bs[i][1]]) for i in indices]
            witnesses.append(row)
    return dict(schema='tno.external_effects.native_evidence.v1', baseline=BASELINE,
        status='STATIC_EVIDENCE', witnesses=witnesses,
        note='Ancient Remnant incoming admission, concrete shared bindings, necklace/phase '
             'state, native healing/persistence and remnant encounter marker only. '
             'Shared/status and Guardian/Monstrosity/Ignis/Harbinger not regenerated. '
             'All offensive goals/payloads, terrain attacks and defeat callbacks deferred.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('jar', type=Path, help='Exact pinned Cataclysm 3.27 JAR')
    evidence = collect(parser.parse_args().jar)
    write_json(SPEC_FILE, specification())
    write_json(EVIDENCE_FILE, evidence)
    print(f'Remnant admission: {len(evidence["witnesses"])} scoped witnesses captured')
