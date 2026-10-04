"""Bounded R2k10a Scylla admission/state/encounter witnesses.

Exact entries from the pinned JAR only. Shared/status/prior boss contracts and
attribute registration are reused; all Scylla offense/payloads are deferred.
"""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

from catalog_common import BASELINE, OUT, read_json, write_json
from classfile import ClassFile, Reader

PKG = 'com/github/L_Ender/cataclysm/'
S = 'entity/InternalAnimationMonster/IABossMonsters/Scylla/Scylla_Entity'
PHASE = S + '$Scylla_EntityPhaseChangeGoal'
SLEEP = S + '$2'
WAKE = S + '$3'
PARRY = S + '$8'
SWING = S + '$HorizontalSwingGoal'
REGISTRY = 'init/ModEntities'
SPEC_FILE = OUT / 'native-specifications/cataclysm-scylla-admission.json'
EVIDENCE_FILE = OUT / 'native-evidence/cataclysm-scylla-admission.json'
METHODS = {
    S: ['hurt', 'CanParryState', 'canBlockFaceSource', 'handleDamageEvent',
        'DamageCap', 'DpsCap', 'RangeLimit', 'NatureRegen', 'scylla',
        'defineSynchedData', 'getEye', 'setEye', 'isFlying', 'setFlying',
        'isPhase', 'setPhase', 'getParryCount', 'setParryCount',
        'getChainAnchor', 'setChainAnchor', 'isSleep', 'getAct', 'setAct',
        'getAnchorUUID', 'setAnchorUUID', 'getAnchor',
        'addAdditionalSaveData', 'readAdditionalSaveData',
        'finalizeSpawn', 'mobInteract', 'canBeSeenAsEnemy',
        'decreaseAirSupply', 'isAffectedByFluids', 'canStandOnFluid',
        'isPushedByFluid'],
    PHASE: ['<init>', 'canUse', 'start', 'stop', 'isInterruptable', 'canContinueToUse'],
    SLEEP: ['<init>', 'canContinueToUse', 'tick'],
    WAKE: ['<init>', 'start', 'stop'],
    PARRY: ['<init>', 'stop'],
    SWING: ['stop'],
    REGISTRY: ['lambda$static$96'],
}
FRAGMENTS = {
    S: {'<init>': [[0, 3], [314, 368], [416, 427]],
        'registerGoals': [[114, 161], [301, 348], [698, 724]],
        'tick': [[0, 1], [109, 144], [293, 307]],
        '<clinit>': [[0, 88]]},
    # Parry consumption only; the rest of the swing tick belongs to R2k10b.
    SWING: {'tick': [[946, 972]]},
    REGISTRY: {'<clinit>': [[1644, 1658]]},
}
RESOURCES = {}


def specification():
    rows = [dict(id='cataclysm:scylla-admission:' + n, mod_key='cataclysm',
        entry=PKG + n + '.class', methods=methods,
        **({'method_fragments': FRAGMENTS[n]} if n in FRAGMENTS else {}))
        for n, methods in sorted(METHODS.items())]
    rows.extend(dict(id='cataclysm:scylla-admission:' + k,
        mod_key='cataclysm', entry=v) for k, v in sorted(RESOURCES.items()))
    return dict(schema='tno.external_effects.native_specification.v1', baseline=BASELINE,
                evidence_specifications=rows)


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
            row = dict(id=spec['id'], mod_key='cataclysm', jar_sha256=target['sha256'],
                entry=spec['entry'], entry_sha256=hashlib.sha256(raw).hexdigest())
            if spec['entry'].endswith('.class'):
                c = ClassFile(raw)
                row.update(class_name=c.name, superclass=c.super,
                           interfaces=c.interfaces, methods=[])
                if spec['entry'] == PKG + S + '.class':
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
                            assert all(any(i['offset'] == v for i in ins) for span in ranges for v in span), (name, ranges)
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
            else:
                row['data'] = json.loads(raw)
            witnesses.append(row)
    return dict(schema='tno.external_effects.native_evidence.v1', baseline=BASELINE,
        status='STATIC_EVIDENCE', witnesses=witnesses,
        note='Scylla concrete facing/parry/phase/sleep incoming order, unchanged shared hurt '
             'bindings, incoming notification, raw native phase/parry/activation/flight state, '
             'combat NBT, configured attributes, spawn-reason activation and native home/heal/player '
             'counter encounter setup only. Phase/sleep/parry goal state fragments required to '
             'close prerequisites included; all offensive motion/payload/terrain/death callbacks '
             'deferred to R2k10b. Shared hierarchy/status/attribute evidence reused; no whole-JAR scan.')



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('jar', type=Path, help='Exact pinned Cataclysm 3.27 JAR')
    evidence = collect(parser.parse_args().jar)
    write_json(SPEC_FILE, specification())
    write_json(EVIDENCE_FILE, evidence)
    print(f'Scylla admission: {len(evidence["witnesses"])} scoped witnesses captured')
