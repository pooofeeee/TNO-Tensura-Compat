"""Missing R2k8b Maledictus offense witnesses from the exact pinned JAR.

Finite entries, offensive goal methods and combat fragments only. Admission,
shared/status contracts, native comparisons and non-damage debris are reused.
"""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

from catalog_common import BASELINE, OUT, read_json, write_json
from classfile import ClassFile, Reader

PKG = 'com/github/L_Ender/cataclysm/'
M = 'entity/InternalAnimationMonster/IABossMonsters/Maledictus/Maledictus_Entity'
A = 'entity/projectile/Phantom_Arrow_Entity'
H = 'entity/projectile/Phantom_Halberd_Entity'
REG = 'init/ModEntities'
SPEC_FILE = OUT / 'native-specifications/cataclysm-maledictus-offense.json'
EVIDENCE_FILE = OUT / 'native-evidence/cataclysm-maledictus-offense.json'
GOALS = {
    '1': ['<init>', 'canUse', 'start', 'stop'],
    '2': ['<init>', 'stop'],
    '3': ['<init>', 'canUse', 'canContinueToUse', 'tick', 'stop'],
    '4': ['<init>', 'tick'],
    '5': ['<init>', 'canUse', 'tick', 'stop'],
    '6': ['<init>', 'canUse', 'start', 'stop'],
    '7': ['<init>', 'canUse', 'start', 'stop'],
    'MaledictusChargeGoal': ['<init>', 'canUse', 'start', 'canContinueToUse', 'tick', 'stop', 'requiresUpdateEveryTick'],
    'MaledictusChargeState': ['<init>', 'start', 'tick', 'stop'],
    'MaledictusGrabGoal': ['<init>', 'canUse', 'start', 'stop', 'canContinueToUse', 'tick', 'requiresUpdateEveryTick'],
    'MaledictusGrabState': ['<init>', 'start', 'canContinueToUse', 'tick', 'stop'],
    'MaledictusSpinSlashes': ['<init>', 'canUse', 'start', 'tick', 'stop', 'requiresUpdateEveryTick'],
    'MaledictusSuccessState': ['<init>', 'start', 'tick', 'stop'],
    'Maledictus_Bow': ['<init>', 'canUse', 'start', 'stop', 'tick', 'requiresUpdateEveryTick'],
    'Maledictus_Flying_Bow': ['<init>', 'canUse', 'start', 'stop', 'tick', 'requiresUpdateEveryTick'],
    'Maledictus_Flying_Smash': ['<init>', 'canUse', 'start', 'stop', 'tick', 'requiresUpdateEveryTick'],
    'Maledictus_Swing': ['<init>', 'canUse', 'tick', 'requiresUpdateEveryTick'],
    'MaledictusfallingState': ['<init>', 'start', 'tick', 'stop'],
    'Uppercut': ['<init>', 'canUse', 'stop', 'tick'],
}
METHODS = {
    M: ['registerGoals', 'DMG', 'AreaAttack', 'ComboAreaAttack', 'Rushattack',
        'uppercut', 'Grab', 'ShieldSmashDamage', 'blockbreak', 'flyingdestroy',
        'blockdestroy', 'blockdestroy2', 'spawnHalberd', 'isAlliedTo',
        'positionRider', 'getControllingPassenger', 'canRiderInteract',
        'shouldRiderSit', 'travel', 'die', 'deathtimer', 'AfterDefeatBoss'],
    A: ['<init>', 'addAdditionalSaveData', 'readAdditionalSaveData',
        'tickDespawn', 'onHitEntity', 'getWeaponItem', 'doPostHurtEffects',
        'getDefaultPickupItem'],
    H: ['<init>', 'defineSynchedData', 'getState', 'setState', 'getDamage',
        'setDamage', 'setCaster', 'getCaster', 'readAdditionalSaveData',
        'addAdditionalSaveData', 'damage'],
    REG: ['lambda$static$31', 'lambda$static$32'],
    **{M + '$' + n: methods for n, methods in GOALS.items()},
}
FRAGMENTS = {
    # R2k8a tick rage decay, no-gravity and health/environment fragments locked.
    M: {'tick': [[4, 76], [212, 345], [379, 388]],
        'aiStep': [[0, 253], [420, 670], [803, 948], [955, 1023],
            [1027, 1447], [1451, 1622], [1775, 1930], [2143, 2264],
            [2440, 3252], [3256, 3337], [3432, 3605], [3634, 3957],
            [3961, 4352], [4502, 4533], [4597, 4668], [4794, 4925]],
        'StrikeHalberd': [[0, 96]],
        'StrikeWindmillHalberd': [[0, 154], [240, 252]],
        'radagonskill': [[0, 155], [192, 198]]},
    A: {'tick': [[0, 55], [66, 222]], 'onHit': [[0, 2]]},
    H: {'tick': [[0, 11], [219, 370]]},
    REG: {'<clinit>': [[539, 570]]},
}
RESOURCES = {
    'terrain-tag': 'data/cataclysm/tags/block/maledictus_immune.json',
    'chandelier-tag': 'data/cataclysm/tags/block/frosted_prison_chandelier.json',
}


def specification():
    rows = [dict(id='cataclysm:maledictus-offense:' + n, mod_key='cataclysm',
        entry=PKG + n + '.class', methods=methods,
        **({'method_fragments': FRAGMENTS[n]} if n in FRAGMENTS else {}))
        for n, methods in sorted(METHODS.items())]
    rows.extend(dict(id='cataclysm:maledictus-offense:' + k,
        mod_key='cataclysm', entry=v) for k, v in sorted(RESOURCES.items()))
    return dict(schema='tno.external_effects.native_specification.v1',
        baseline=BASELINE, evidence_specifications=rows)


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
            row = dict(id=spec['id'], mod_key='cataclysm',
                jar_sha256=target['sha256'], entry=spec['entry'],
                entry_sha256=hashlib.sha256(raw).hexdigest())
            if spec['entry'].endswith('.class'):
                c = ClassFile(raw)
                row.update(class_name=c.name, superclass=c.super,
                           interfaces=c.interfaces, methods=[])
                if spec['entry'] in [PKG + n + '.class' for n in [M, A, H]]:
                    row['declared_method_names'] = sorted({m['name'] for m in c.methods})
                for name in spec['methods'] + list(spec.get('method_fragments', {})):
                    matches = [m for m in c.methods if m['name'] == name]
                    assert matches, (spec['entry'], name)
                    for m in matches:
                        code = m.get('code', b'')
                        ins = list(c.instructions(code))
                        ranges = spec.get('method_fragments', {}).get(name)
                        if ranges:
                            ins = [i for i in ins if any(a <= i['offset'] <= b for a, b in ranges)]
                            assert all(any(i['offset'] == v for i in ins)
                                       for r in ranges for v in r), (spec['entry'], name, ranges)
                        row['methods'].append(dict(name=name, descriptor=m['descriptor'],
                            code_sha256=hashlib.sha256(code).hexdigest(), instructions=ins,
                            **({'instruction_offset_ranges': ranges} if ranges else {})))
                if spec['entry'] == PKG + REG + '.class':
                    reader = Reader(next(data for name, data in c.attributes if name == 'BootstrapMethods'))
                    bs = [(reader.u2(), [reader.u2() for _ in range(reader.u2())])
                          for _ in range(reader.u2())]
                    indices = sorted({int(i['operand'].split('#')[1].split(':')[0])
                        for m in row['methods'] for i in m['instructions'] if i['opcode'] == '0xba'})
                    row['registration_bootstraps'] = [dict(index=i, handle=c.resolve(bs[i][0]),
                        arguments=[c.resolve(a) for a in bs[i][1]]) for i in indices]
            else:
                row['data'] = json.loads(raw)
            witnesses.append(row)
    return dict(schema='tno.external_effects.native_evidence.v1', baseline=BASELINE,
        status='STATIC_EVIDENCE', witnesses=witnesses,
        note='Missing Maledictus offensive goals, offense/terrain/death fragments, '
             'two owned phantom payloads and their exact registration/terrain tags only. '
             'Locked admission/shared/status/prior bosses, native comparisons, damage '
             'types/factories/team tag and non-damage debris reused. Purely visual bodies excluded; '
             'incidental visual callsites retained only where needed for combat ordering. '
             'No runtime, Stage or whole-mod completeness claim.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('jar', type=Path, help='Exact pinned Cataclysm 3.27 JAR')
    evidence = collect(parser.parse_args().jar)
    write_json(SPEC_FILE, specification())
    write_json(EVIDENCE_FILE, evidence)
    print(f'Maledictus offense: {len(evidence["witnesses"])} scoped witnesses captured')
