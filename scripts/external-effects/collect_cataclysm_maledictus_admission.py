"""Bounded R2k8a Maledictus admission/state/encounter witnesses.

Read exact entries from the pinned Cataclysm JAR. Reuse locked parent bodies,
attribute registration and comparison evidence; do not capture offense.
"""
import argparse
import hashlib
from pathlib import Path
import zipfile

from catalog_common import BASELINE, OUT, read_json, write_json
from classfile import ClassFile, Reader

PKG = 'com/github/L_Ender/cataclysm/'
M = 'entity/InternalAnimationMonster/IABossMonsters/Maledictus/Maledictus_Entity'
TOMB = 'blockentities/Cursed_tombstone_Entity'
BLOCK = 'blocks/Cursed_Tombstone_Block'
REGISTRY = 'init/ModEntities'
SPEC_FILE = OUT / 'native-specifications/cataclysm-maledictus-admission.json'
EVIDENCE_FILE = OUT / 'native-evidence/cataclysm-maledictus-admission.json'
METHODS = {
    M: ['hurt', 'DamageCap', 'DpsCap', 'DpsMulti', 'RangeLimit', 'NatureRegen',
        'defineSynchedData', 'getWeapon', 'setWeapon', 'isFlying', 'setFlying',
        'getTombstoneDirection', 'setTombstoneDirection', 'getRageMeter',
        'setRageMeter', 'addAdditionalSaveData', 'readAdditionalSaveData',
        'finalizeSpawn', 'isHalfHealth', 'isQuarterHealth', 'maledictus',
        'decreaseAirSupply', 'causeFallDamage', 'isAffectedByFluids', 'isPushedByFluid'],
    TOMB: ['<init>', 'loadAdditional', 'saveAdditional'],
    BLOCK: ['<init>', 'useItemOn', 'newBlockEntity', 'getTicker'],
    REGISTRY: ['lambda$static$87'],
}
FRAGMENTS = {
    M: {'<init>': [[0, 3], [470, 498]],
        # Parent tick, server rage decay and flight/gravity prerequisite only.
        # Passenger control, display, attack cooldowns and terrain execution deferred.
        'tick': [[0, 1], [79, 86], [125, 166], [348, 376]]},
    TOMB: {'commonTick': [[0, 73], [90, 113], [466, 508], [526, 776]]},
    REGISTRY: {'<clinit>': [[1491, 1505]]},
}


def specification():
    return dict(schema='tno.external_effects.native_specification.v1', baseline=BASELINE,
        evidence_specifications=[dict(id='cataclysm:maledictus-admission:' + name,
            mod_key='cataclysm', entry=PKG + name + '.class', methods=methods,
            **({'method_fragments': FRAGMENTS[name]} if name in FRAGMENTS else {}))
            for name, methods in sorted(METHODS.items())])


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
            if spec['entry'] == PKG + M + '.class':
                row['declared_method_names'] = sorted({m['name'] for m in c.methods})
                row['declared_fields'] = [dict(name=f['name'], descriptor=f['descriptor'])
                                          for f in c.fields]
            for name in spec['methods'] + list(spec.get('method_fragments', {})):
                matches = [m for m in c.methods if m['name'] == name]
                assert matches, (spec['entry'], name)
                for m in matches:
                    code = m.get('code', b'')
                    instructions = list(c.instructions(code))
                    ranges = spec.get('method_fragments', {}).get(name)
                    if ranges:
                        instructions = [i for i in instructions if any(
                            a <= i['offset'] <= b for a, b in ranges)]
                        assert all(any(i['offset'] == boundary for i in instructions)
                                   for span in ranges for boundary in span), (name, ranges)
                    row['methods'].append(dict(name=name, descriptor=m['descriptor'],
                        code_sha256=hashlib.sha256(code).hexdigest(), instructions=instructions,
                        **({'instruction_offset_ranges': ranges} if ranges else {})))
            if spec['entry'] in [PKG + name + '.class' for name in [REGISTRY, BLOCK]]:
                reader = Reader(next(data for name, data in c.attributes
                                     if name == 'BootstrapMethods'))
                bootstraps = [(reader.u2(), [reader.u2() for _ in range(reader.u2())])
                              for _ in range(reader.u2())]
                indices = sorted({int(i['operand'].split('#')[1].split(':')[0])
                    for m in row['methods'] for i in m['instructions'] if i['opcode'] == '0xba'})
                row['registration_bootstraps'] = [dict(index=i,
                    handle=c.resolve(bootstraps[i][0]),
                    arguments=[c.resolve(a) for a in bootstraps[i][1]]) for i in indices]
            witnesses.append(row)
    return dict(schema='tno.external_effects.native_evidence.v1', baseline=BASELINE,
        status='STATIC_EVIDENCE', witnesses=witnesses,
        note='Maledictus incoming hurt, concrete shared bindings, native environment '
             'admission, raw state/health prerequisites, saved state and exact cursed '
             'tombstone encounter only. Locked hierarchy bodies and attribute event reused. '
             'All offensive selection/goals/payloads, rage gain/damage, passenger control, '
             'terrain-response execution and defeat callbacks deferred to R2k8b.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('jar', type=Path, help='Exact pinned Cataclysm 3.27 JAR')
    evidence = collect(parser.parse_args().jar)
    write_json(SPEC_FILE, specification())
    write_json(EVIDENCE_FILE, evidence)
    print(f'Maledictus admission: {len(evidence["witnesses"])} scoped witnesses captured')
