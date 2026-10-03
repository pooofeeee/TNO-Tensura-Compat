"""Missing R2k6b Harbinger offense witnesses from the exact pinned JAR.

Explicit methods/fragments only. Locked admission, shared/status, completed
bosses, native projectile/explosion and non-damage debris are reused.
"""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

from catalog_common import BASELINE, OUT, read_json, write_json
from classfile import ClassFile, Reader
from collect_cataclysm_harbinger_admission import H, PKG, REGISTRY

M = 'entity/projectile/Wither_Missile_Entity'
HM = 'entity/projectile/Wither_Homing_Missile_Entity'
HOW = 'entity/projectile/Wither_Howitzer_Entity'
L = 'entity/projectile/Laser_Beam_Entity'
D = 'entity/projectile/Death_Laser_Beam_Entity'
SM = 'entity/effect/Wither_Smoke_Effect_Entity'
TIMER = 'client/tool/ControlledAnimation'
TARGET = 'entity/AI/HurtByNearestTargetGoal'
SPEC_FILE = OUT / 'native-specifications/cataclysm-harbinger-offense.json'
EVIDENCE_FILE = OUT / 'native-evidence/cataclysm-harbinger-offense.json'
METHODS = {
    H: ['getAnimations', 'isAlliedTo', 'canBeAffected', 'canBePushedByEntity',
        'repelEntities', 'blockbreak', 'destroyBlock', 'destoryblock2',
        'performRangedAttack', 'getHeadX', 'getHeadY', 'getHeadZ',
        'getDeathAnimation', 'onDeathAIUpdate', 'AfterDefeatBoss',
        'lambda$static$0', 'access$000'],
    H + '$ChargeGoal': ['<init>', 'start', 'tick', 'stop'],
    H + '$DeathLaserGoal': ['<init>', 'start', 'tick'],
    H + '$LaunchGoal': ['<init>', 'start', 'tick', 'launch'],
    H + '$MissileLaunchGoal': ['<init>', 'start', 'tick', 'mlaunch',
        'getLauncherX', 'getLauncherY', 'getLauncherZ'],
    H + '$MissileLaunchGoal2': ['<init>', 'start', 'tick', 'mlaunch',
        'getLauncherX', 'getLauncherY', 'getLauncherZ'],
    TARGET: ['<init>', 'canUse', 'canContinueToUse'],
    M: ['<init>', 'defineSynchedData', 'getDamage', 'setDamage',
        'getClipType', 'onHitEntity', 'onHit', 'canHitEntity', 'getInertia',
        'addAdditionalSaveData', 'readAdditionalSaveData', 'isPickable',
        'getPickRadius', 'hurt', 'assignDirectionalMovement', 'onDeflection'],
    HM: ['<init>', 'defineSynchedData', 'getDamage', 'setDamage', 'setFuse',
        'getFuse', 'onHitEntity', 'onHitBlock', 'onHit', 'canHitEntity',
        'getInertia', 'addAdditionalSaveData', 'readAdditionalSaveData',
        'isPickable', 'getPickRadius', 'hurt', 'assignDirectionalMovement', 'onDeflection'],
    HOW: ['<init>', 'defineSynchedData', 'setRadius', 'getRadius', 'onHitEntity',
        'onHit', 'addAdditionalSaveData', 'readAdditionalSaveData', 'getDefaultGravity'],
    L: ['<init>', 'defineSynchedData', 'getDamage', 'setDamage', 'getClipType',
        'tick', 'onHitEntity', 'onHitBlock', 'onHit', 'canHitEntity', 'getInertia',
        'addAdditionalSaveData', 'readAdditionalSaveData', 'isPickable',
        'getPickRadius', 'hurt', 'assignDirectionalMovement', 'onDeflection'],
    D: ['<init>', 'defineSynchedData', 'getDamage', 'setDamage', 'getHpDamage',
        'setHpDamage', 'getYaw', 'setYaw', 'getPitch', 'setPitch', 'getDuration',
        'setDuration', 'getCasterID', 'setCasterID', 'getFire', 'setFire',
        'readAdditionalSaveData', 'addAdditionalSaveData', 'calculateEndPos',
        'raytraceEntities', 'updateWithHarbinger', 'push', 'canBeCollidedWith', 'isPushable'],
    D + '$LaserbeamHitResult': ['<init>', 'setBlockHit', 'addEntityHit'],
    SM: ['<init>', 'defineSynchedData', 'setRadius', 'refreshDimensions',
        'getRadius', 'setWaiting', 'isWaiting', 'getDuration', 'setDuration',
        'damage', 'getRadiusOnUse', 'setRadiusOnUse', 'getRadiusPerTick',
        'setRadiusPerTick', 'getDurationOnUse', 'setDurationOnUse', 'getWaitTime',
        'setWaitTime', 'setOwner', 'getOwner', 'readAdditionalSaveData',
        'addAdditionalSaveData', 'onSyncedDataUpdated', 'getDimensions'],
    # This otherwise visual timer controls native beam discard and damage lifetime.
    TIMER: ['<init>', 'getTimer'],
    REGISTRY: ['lambda$static$43', 'lambda$static$51', 'lambda$static$55',
        'lambda$static$56', 'lambda$static$57', 'lambda$static$58'],
}
FRAGMENTS = {
    H: {'registerGoals': [[16, 250]], '<clinit>': [[0, 46], [149, 175]],
        'aiStep': [[0, 26], [150, 880], [926, 945]],
        'customServerAiStep': [[58, 371], [455, 480]]},
    M: {'tick': [[0, 141], [218, 220], [313, 355]]},
    HM: {'tick': [[0, 136], [214, 217], [263, 606]]},
    HOW: {'tick': [[0, 1]]},  # inherited ballistic tick, no trail/particles
    D: {'tick': [[0, 125], [142, 341], [349, 933]]},
    SM: {'tick': [[0, 21], [197, 343]]},
    REGISTRY: {'<clinit>': [[746, 757], [882, 893], [950, 1012]]},
}
DESCRIPTORS = {TIMER: {'increaseTimer': '()V', 'decreaseTimer': '()V'}}
METHODS[TIMER] += list(DESCRIPTORS[TIMER])
RESOURCES = {
    'immune-tag': 'data/cataclysm/tags/block/harbinger_immune.json',
    'glass-tag': 'data/cataclysm/tags/block/cm_glass.json',
}


def specification():
    rows = [dict(id='cataclysm:harbinger-offense:' + n, mod_key='cataclysm',
        entry=PKG + n + '.class', methods=methods,
        **({'method_fragments': FRAGMENTS[n]} if n in FRAGMENTS else {}),
        **({'method_descriptors': DESCRIPTORS[n]} if n in DESCRIPTORS else {}))
        for n, methods in sorted(METHODS.items())]
    rows.extend(dict(id='cataclysm:harbinger-offense:' + k, mod_key='cataclysm', entry=v)
                for k, v in sorted(RESOURCES.items()))
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
            row = dict(id=spec['id'], mod_key='cataclysm', jar_sha256=target['sha256'],
                       entry=spec['entry'], entry_sha256=hashlib.sha256(raw).hexdigest())
            if spec['entry'].endswith('.class'):
                c = ClassFile(raw)
                row.update(class_name=c.name, superclass=c.super, interfaces=c.interfaces, methods=[])
                if spec['entry'] in [PKG + n + '.class' for n in [H, M, HM, HOW, L, D, SM]]:
                    row['declared_method_names'] = sorted({m['name'] for m in c.methods})
                for name in spec['methods'] + list(spec.get('method_fragments', {})):
                    matches = [m for m in c.methods if m['name'] == name and
                               (name not in spec.get('method_descriptors', {}) or
                                m['descriptor'] == spec['method_descriptors'][name])]
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
                    row['registration_bootstraps'] = [dict(index=i, handle=c.resolve(bs[i][0]),
                        arguments=[c.resolve(a) for a in bs[i][1]]) for i in sorted({int(ins['operand'].split('#')[1].split(':')[0])
                            for m in row['methods'] for ins in m['instructions']
                            if ins['opcode'] == '0xba'})]
            else:
                row['data'] = json.loads(raw)
            witnesses.append(row)
    return dict(schema='tno.external_effects.native_evidence.v1', baseline=BASELINE,
        status='STATIC_EVIDENCE', witnesses=witnesses,
        note='Missing Harbinger offense, six directly owned payloads and beam-lifecycle timer only. '
             'Locked R2k6a/shared/status/Guardian/Monstrosity/Ignis and native comparisons '
             'not regenerated. No runtime, Stage or whole-mod completeness claim.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('jar', type=Path, help='Exact pinned Cataclysm 3.27 JAR')
    evidence = collect(parser.parse_args().jar)
    write_json(SPEC_FILE, specification())
    write_json(EVIDENCE_FILE, evidence)
    print(f'Harbinger offense: {len(evidence["witnesses"])} scoped witnesses captured')
