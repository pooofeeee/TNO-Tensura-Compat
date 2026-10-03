"""Capture only missing Ignis admission/state/encounter witnesses (R2k5a).

Explicit pinned entries and method fragments only; no offense/payload scan.
Shared/Guardian/Monstrosity and native shield/hurt contracts are reused.
"""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

from catalog_common import BASELINE, OUT, read_json, write_json
from classfile import ClassFile, Reader

PKG = 'com/github/L_Ender/cataclysm/'
I = 'entity/AnimationMonster/BossMonsters/Ignis_Entity'
BASE = 'entity/AnimationMonster/BossMonsters/LLibrary_Boss_Monster'
MM = 'entity/AnimationMonster/LLibrary_Monster'
AM = 'entity/etc/Animation_Monsters'
GOAL = 'entity/AnimationMonster/AI/AttackAnimationGoal1'
ALTAR = 'blockentities/AltarOfFire_Block_Entity'
BLOCK = 'blocks/Altar_Of_Fire_Block'
REGISTRY = 'init/ModEntities'
SPEC_FILE = OUT / 'native-specifications/cataclysm-ignis-admission.json'
EVIDENCE_FILE = OUT / 'native-evidence/cataclysm-ignis-admission.json'
METHODS = {
    I: ['<init>', 'hurt', 'canBlockDamageSource', 'defineSynchedData',
        'addAdditionalSaveData', 'readAdditionalSaveData', 'setIsBlocking',
        'getIsBlocking', 'setIsShield', 'getIsShield', 'setIsSword', 'getIsSword',
        'setIsShieldBreak', 'getIsShieldBreak', 'setShieldDurability',
        'getShieldDurability', 'setShowShield', 'getShowShield', 'setBossPhase',
        'getBossPhase', 'ignis', 'DamageCap', 'DpsCap', 'RangeLimit', 'NatureRegen',
        'finalizeSpawn'],
    # Declaration-only absence checks. Already captured shared bodies stay cold.
    BASE: [], AM: [], MM: [],
    GOAL: ['<init>', 'tick'],
    ALTAR: ['<init>', 'commonTick', 'getItem', 'loadAdditional', 'saveAdditional'],
    BLOCK: ['getTicker'],
    REGISTRY: ['lambda$static$8'],
}
FRAGMENTS = {
    I: {
        'registerGoals': [[223, 242], [267, 286], [444, 464]],
        '<clinit>': [[48, 53], [88, 93], [225, 230]],
    },
    ALTAR: {'tick': [[0, 45], [98, 266]]},
    REGISTRY: {'<clinit>': [[148, 162]]},
}


def specification():
    rows = [dict(id='cataclysm:ignis-admission:' + n, mod_key='cataclysm',
        entry=PKG + n + '.class', methods=names,
        **({'method_fragments': FRAGMENTS[n]} if n in FRAGMENTS else {}))
        for n, names in sorted(METHODS.items())]
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
            if spec['entry'] in [PKG + n + '.class' for n in [I, BASE, MM, AM, ALTAR]]:
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
            if spec['entry'] in [PKG + REGISTRY + '.class', PKG + BLOCK + '.class']:
                r = Reader(next(data for name, data in c.attributes if name == 'BootstrapMethods'))
                bs = [(r.u2(), [r.u2() for _ in range(r.u2())]) for _ in range(r.u2())]
                indices = [105, 122] if spec['entry'] == PKG + REGISTRY + '.class' else [
                    int(i['operand'].split('#')[1].split(':')[0])
                    for m in row['methods'] for i in m['instructions'] if i['opcode'] == '0xba']
                row['registration_bootstraps'] = [dict(index=i, handle=c.resolve(bs[i][0]),
                    arguments=[c.resolve(a) for a in bs[i][1]]) for i in indices]
            witnesses.append(row)
    return dict(schema='tno.external_effects.native_evidence.v1', baseline=BASELINE,
        status='STATIC_EVIDENCE', witnesses=witnesses,
        note='Ignis incoming/shield/phase/persistence/altar prerequisites only. '
             'Existing STUN Ignis tick/aiStep and shared animation helpers reused unchanged; '
             'shared/status/Guardian/Monstrosity bodies not recaptured. '
             'Offense, phase damage, shield explosions, projectiles and outcome callbacks deferred.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('jar', type=Path, help='Exact pinned Cataclysm 3.27 JAR')
    evidence = collect(parser.parse_args().jar)
    write_json(SPEC_FILE, specification())
    write_json(EVIDENCE_FILE, evidence)
    print(f'Ignis admission: {len(evidence["witnesses"])} scoped witnesses captured')
