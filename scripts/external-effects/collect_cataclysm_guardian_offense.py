"""Capture only missing R2k3b methods from the exact pinned Cataclysm JAR.

Guardian tick/AreaAttack, nearby-recipient/shield helpers, shared lifecycle,
status contracts and loader/vanilla witnesses remain immutable reused inputs.
No class discovery, whole-JAR scan, source generation or runtime execution.
"""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

from catalog_common import BASELINE, OUT, read_json, write_json
from classfile import ClassFile

PKG = 'com/github/L_Ender/cataclysm/'
G = 'entity/AnimationMonster/BossMonsters/Ender_Guardian_Entity'
B = 'entity/projectile/Ender_Guardian_Bullet_Entity'
R = 'entity/projectile/Void_Rune_Entity'
V = 'entity/effect/Void_Vortex_Entity'
SPEC_FILE = OUT / 'native-specifications/cataclysm-guardian-offense.json'
EVIDENCE_FILE = OUT / 'native-evidence/cataclysm-guardian-offense.json'

# Explicit names only. Already captured methods are deliberately absent.
METHODS = {
    G: ['getRandomAttack', 'aiStep', 'StrikeRune', 'MassDestruction',
        'BlockBreaking', 'launch', 'GravityPull', 'StompAttack', 'RageAttack',
        'spawnFangs', 'spawnVortex', 'Bulletpattern', 'isAlliedTo',
        'canBePushedByEntity', 'onDeathAIUpdate', 'AfterDefeatBoss',
        'Respawner', 'getDeathAnimation', '<clinit>'],
    G + '$PunchAttackGoal': ['<init>', 'test', 'tick'],
    G + '$StompAttackGoal': ['<init>', 'test', 'tick'],
    G + '$UppercutAndBulletGoal': ['<init>', 'tick'],
    G + '$RageUppercut': ['<init>', 'tick'],
    G + '$RocketPunchGoal': ['<init>', 'tick'],
    G + '$VoidVortexGoal': ['<init>', 'tick'],
    B: ['<init>', 'setUp', 'tick', 'lambda$tick$0', 'onHit', 'onHitEntity',
        'onHitBlock', 'hurt', 'canBeCollidedWith', 'addAdditionalSaveData',
        'readAdditionalSaveData'],
    R: ['<init>', 'defineSynchedData', 'getDamage', 'setDamage', 'setCaster',
        'getCaster', 'tick', 'damage', 'addAdditionalSaveData',
        'readAdditionalSaveData'],
    V: ['<init>', 'defineSynchedData', 'tick', 'getLifespan', 'setLifespan',
        'getCasterID', 'setCasterID', 'setOwner', 'getOwner',
        'addAdditionalSaveData', 'readAdditionalSaveData'],
    'entity/etc/Animation_Monsters': ['getAngleBetweenEntities', 'repelEntities'],
    'blockentities/Boss_Respawn_Spawner_Block_Entity': [
        '<init>', 'tick', 'anyPlayerInRange', 'spawnMyBoss', 'getRange',
        'setTheItem', 'setEntityId', 'onHit', 'loadAdditional', 'saveAdditional'],
    'blocks/Boss_Respawn_Spawner_Block': ['<init>', 'getTicker', 'useItemOn'],
}


def specification():
    rows = [dict(id='cataclysm:guardian-offense:' + name,
                 mod_key='cataclysm', entry=PKG + name + '.class', methods=names)
            for name, names in sorted(METHODS.items())]
    rows.append(dict(id='cataclysm:guardian-offense:destroy-tag',
                     mod_key='cataclysm',
                     entry='data/cataclysm/tags/block/ender_guardian_can_destroy.json'))
    return dict(schema='tno.external_effects.native_specification.v1',
                baseline=BASELINE, evidence_specifications=rows)


def collect(jar_path):
    target = next(t for t in read_json(OUT / 'jar-inventory.json')['targets']
                  if t['key'] == 'cataclysm')
    jar_path = Path(jar_path)
    assert hashlib.sha256(jar_path.read_bytes()).hexdigest() == target['sha256']
    assert jar_path.stat().st_size == target['size_bytes']
    witnesses = []
    with zipfile.ZipFile(jar_path) as jar:
        for spec in specification()['evidence_specifications']:
            data = jar.read(spec['entry'])
            row = dict(id=spec['id'], mod_key='cataclysm',
                       jar_sha256=target['sha256'], entry=spec['entry'],
                       entry_sha256=hashlib.sha256(data).hexdigest())
            if spec['entry'].endswith('.class'):
                parsed = ClassFile(data)
                row.update(class_name=parsed.name, superclass=parsed.super,
                           interfaces=parsed.interfaces, methods=[])
                for name in spec['methods']:
                    selected = [m for m in parsed.methods if m['name'] == name]
                    assert selected, (spec['entry'], name)
                    for m in selected:
                        code = m.get('code', b'')
                        row['methods'].append(dict(
                            name=name, descriptor=m['descriptor'],
                            code_sha256=hashlib.sha256(code).hexdigest(),
                            instructions=list(parsed.instructions(code))))
            else:
                row['data'] = json.loads(data)
            witnesses.append(row)
    return dict(schema='tno.external_effects.native_evidence.v1',
                baseline=BASELINE, status='STATIC_EVIDENCE', witnesses=witnesses,
                note='Exact pinned class/method bytes for Guardian offense only. '
                     'Reused evidence is not regenerated. Static evidence is not '
                     'runtime validation, Stage eligibility or whole-mod completeness.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('jar', type=Path, help='Exact pinned Cataclysm 3.27 JAR')
    args = parser.parse_args()
    evidence = collect(args.jar)
    write_json(SPEC_FILE, specification())
    write_json(EVIDENCE_FILE, evidence)
    print(f'Guardian offense: {len(evidence["witnesses"])} scoped witnesses captured')
