"""Bounded R2k9b Leviathan offense witnesses from the exact pinned JAR.

Previously captured admission/status/beam ticks and shared/native contracts are
reused. Only finite owned entries, offensive goals and missing combat fragments.
"""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

from catalog_common import BASELINE, OUT, read_json, write_json
from classfile import ClassFile, Reader

PKG = 'com/github/L_Ender/cataclysm/'
FAMILY = 'entity/AnimationMonster/BossMonsters/The_Leviathan/'
L = FAMILY + 'The_Leviathan_Entity'
REG = 'init/ModEntities'
WORLD = 'world/data/CMWorldData'
SPEC_FILE = OUT / 'native-specifications/cataclysm-leviathan-offense.json'
EVIDENCE_FILE = OUT / 'native-evidence/cataclysm-leviathan-offense.json'
GOALS = ['LeviathanAttackGoal',
 'LeviathanGrabAttackGoal',
 'LeviathanAbyssDimensionAttackGoal',
 'LeviathanStunGoal',
 'LeviathanGrabBiteAttackGoal',
 'LeviathanBiteAttackGoal',
 'LeviathanPhase2Goal',
 'LeviathanTailWhipsAttackGoal',
 'LeviathanTentacleAttackGoal',
 'LeviathanBlastAttackGoal',
 'LeviathanBlastFireAttackGoal',
 'LeviathanAbyssBlastPortalAttackGoal',
 'LeviathanRushAttackGoal',
 'LeviathanTentacleHoldAttackGoal',
 'LeviathanTentacleHoldBlastAttackGoal',
 'LeviathanMineAttackGoal']
METHODS = {'entity/AnimationMonster/BossMonsters/The_Leviathan/Abyss_Blast_Entity': ['<init>',
                                                                           'defineSynchedData',
                                                                           'getDamage',
                                                                           'setDamage',
                                                                           'getHpDamage',
                                                                           'setHpDamage',
                                                                           'getYaw',
                                                                           'setYaw',
                                                                           'getPitch',
                                                                           'setPitch',
                                                                           'getDuration',
                                                                           'setDuration',
                                                                           'getBeamDirection',
                                                                           'setBeamDirection',
                                                                           'getCasterID',
                                                                           'setCasterID',
                                                                           'readAdditionalSaveData',
                                                                           'addAdditionalSaveData',
                                                                           'calculateEndPos',
                                                                           'raytraceEntities',
                                                                           'push',
                                                                           'canBeCollidedWith',
                                                                           'isPushable',
                                                                           'updateWithHarbinger'],
 'entity/AnimationMonster/BossMonsters/The_Leviathan/Abyss_Blast_Portal_Entity': ['<init>',
                                                                                  'defineSynchedData',
                                                                                  'getCaster',
                                                                                  'setCaster',
                                                                                  'getDamage',
                                                                                  'setDamage',
                                                                                  'getHpDamage',
                                                                                  'setHpDamage',
                                                                                  'isActivate',
                                                                                  'setActivate',
                                                                                  'addAdditionalSaveData',
                                                                                  'readAdditionalSaveData'],
 'entity/AnimationMonster/BossMonsters/The_Leviathan/Abyss_Mine_Entity': ['<init>',
                                                                          'defineSynchedData',
                                                                          'getCaster',
                                                                          'setCaster',
                                                                          'isActivate',
                                                                          'setActivate',
                                                                          'addAdditionalSaveData',
                                                                          'readAdditionalSaveData',
                                                                          'explode'],
 'entity/AnimationMonster/BossMonsters/The_Leviathan/Abyss_Orb_Entity': ['<init>',
                                                                         'defineSynchedData',
                                                                         'getDamage',
                                                                         'setDamage',
                                                                         'addAdditionalSaveData',
                                                                         'readAdditionalSaveData',
                                                                         'getTracking',
                                                                         'setTracking',
                                                                         'setUp',
                                                                         'onHitEntity',
                                                                         'onHitBlock',
                                                                         'onHit',
                                                                         'canHitEntity',
                                                                         'getInertia',
                                                                         'isPickable',
                                                                         'hurt'],
 'entity/AnimationMonster/BossMonsters/The_Leviathan/Abyss_Portal_Entity': ['<init>',
                                                                            'defineSynchedData',
                                                                            'getLifespan',
                                                                            'setLifespan',
                                                                            'getEntrance',
                                                                            'setEntrance',
                                                                            'setDestination',
                                                                            'getDestination',
                                                                            'createAndSetSister',
                                                                            'link',
                                                                            'getSister',
                                                                            'getSisterId',
                                                                            'setSisterId',
                                                                            'addAdditionalSaveData',
                                                                            'readAdditionalSaveData'],
 'entity/AnimationMonster/BossMonsters/The_Leviathan/Dimensional_Rift_Entity': ['<init>',
                                                                                'defineSynchedData',
                                                                                'getStage',
                                                                                'setStage',
                                                                                'getLifespan',
                                                                                'setLifespan',
                                                                                'getOwner',
                                                                                'setOwner',
                                                                                'addAdditionalSaveData',
                                                                                'readAdditionalSaveData',
                                                                                'damage',
                                                                                'berserkBlockBreaking'],
 'entity/AnimationMonster/BossMonsters/The_Leviathan/Portal_Abyss_Blast_Entity': ['<init>',
                                                                                  'defineSynchedData',
                                                                                  'getDamage',
                                                                                  'setDamage',
                                                                                  'getHpDamage',
                                                                                  'setHpDamage',
                                                                                  'getYaw',
                                                                                  'setYaw',
                                                                                  'getPitch',
                                                                                  'setPitch',
                                                                                  'getDuration',
                                                                                  'setDuration',
                                                                                  'getBeamDirection',
                                                                                  'setBeamDirection',
                                                                                  'getCasterID',
                                                                                  'setCasterID',
                                                                                  'readAdditionalSaveData',
                                                                                  'addAdditionalSaveData',
                                                                                  'calculateEndPos',
                                                                                  'raytraceEntities',
                                                                                  'push',
                                                                                  'canBeCollidedWith',
                                                                                  'isPushable'],
 'entity/AnimationMonster/BossMonsters/The_Leviathan/The_Leviathan_Entity': ['registerGoals',
                                                                             'getAnimations',
                                                                             'travel',
                                                                             'getRandomTantalcleStrike',
                                                                             'isAlliedTo',
                                                                             'roarDarkness',
                                                                             'AfterDefeatBoss',
                                                                             'shootAbyssOrb',
                                                                             'launch',
                                                                             'blockbreak',
                                                                             'blockbreak2',
                                                                             'Tentacleattack',
                                                                             'TentacleHoldattack',
                                                                             'positionRider',
                                                                             'shouldRiderSit',
                                                                             'getControllingPassenger',
                                                                             'canRide',
                                                                             'raytraceEntities',
                                                                             'getTongueUUID',
                                                                             'setTongueUUID',
                                                                             'getTongue',
                                                                             'createStuckPortal',
                                                                             'createPortal2',
                                                                             'resetPortalLogic',
                                                                             'teleportTo',
                                                                             'switchNavigator',
                                                                             'shouldEnterWater',
                                                                             'shouldLeaveWater',
                                                                             'shouldStopMoving',
                                                                             'getWaterSearchRange',
                                                                             'setPartPosition',
                                                                             'getTonguePosition',
                                                                             'getDeathAnimation'],
 'entity/AnimationMonster/BossMonsters/The_Leviathan/The_Leviathan_Entity$LeviathanAbyssBlastPortalAttackGoal': ['<init>',
                                                                                                                 'spawnUnderPortal',
                                                                                                                 'start',
                                                                                                                 'stop',
                                                                                                                 'tick'],
 'entity/AnimationMonster/BossMonsters/The_Leviathan/The_Leviathan_Entity$LeviathanAbyssDimensionAttackGoal': ['<init>',
                                                                                                               'getClosestDimensionalRift',
                                                                                                               'start',
                                                                                                               'stop',
                                                                                                               'tick'],
 'entity/AnimationMonster/BossMonsters/The_Leviathan/The_Leviathan_Entity$LeviathanAttackGoal': ['<init>',
                                                                                                 'canContinueToUse',
                                                                                                 'canUse',
                                                                                                 'requiresUpdateEveryTick',
                                                                                                 'start',
                                                                                                 'stop',
                                                                                                 'tick'],
 'entity/AnimationMonster/BossMonsters/The_Leviathan/The_Leviathan_Entity$LeviathanBiteAttackGoal': ['<init>',
                                                                                                     'start',
                                                                                                     'stop',
                                                                                                     'tick'],
 'entity/AnimationMonster/BossMonsters/The_Leviathan/The_Leviathan_Entity$LeviathanBlastAttackGoal': ['<init>',
                                                                                                      'start',
                                                                                                      'stop',
                                                                                                      'tick'],
 'entity/AnimationMonster/BossMonsters/The_Leviathan/The_Leviathan_Entity$LeviathanBlastFireAttackGoal': ['<init>',
                                                                                                          'start',
                                                                                                          'stop',
                                                                                                          'tick'],
 'entity/AnimationMonster/BossMonsters/The_Leviathan/The_Leviathan_Entity$LeviathanGrabAttackGoal': ['<init>',
                                                                                                     'start',
                                                                                                     'stop',
                                                                                                     'tick'],
 'entity/AnimationMonster/BossMonsters/The_Leviathan/The_Leviathan_Entity$LeviathanGrabBiteAttackGoal': ['<init>',
                                                                                                         'start',
                                                                                                         'stop',
                                                                                                         'tick'],
 'entity/AnimationMonster/BossMonsters/The_Leviathan/The_Leviathan_Entity$LeviathanMineAttackGoal': ['<init>',
                                                                                                     'spawnMines',
                                                                                                     'start',
                                                                                                     'stop',
                                                                                                     'tick'],
 'entity/AnimationMonster/BossMonsters/The_Leviathan/The_Leviathan_Entity$LeviathanMoveController': ['<init>',
                                                                                                     'tick'],
 'entity/AnimationMonster/BossMonsters/The_Leviathan/The_Leviathan_Entity$LeviathanPhase2Goal': ['<init>',
                                                                                                 'start',
                                                                                                 'stop',
                                                                                                 'tick'],
 'entity/AnimationMonster/BossMonsters/The_Leviathan/The_Leviathan_Entity$LeviathanRushAttackGoal': ['<init>',
                                                                                                     'start',
                                                                                                     'stop',
                                                                                                     'tick'],
 'entity/AnimationMonster/BossMonsters/The_Leviathan/The_Leviathan_Entity$LeviathanStunGoal': ['<init>',
                                                                                               'start',
                                                                                               'stop',
                                                                                               'tick'],
 'entity/AnimationMonster/BossMonsters/The_Leviathan/The_Leviathan_Entity$LeviathanTailWhipsAttackGoal': ['<init>',
                                                                                                          'start',
                                                                                                          'stop',
                                                                                                          'tick'],
 'entity/AnimationMonster/BossMonsters/The_Leviathan/The_Leviathan_Entity$LeviathanTentacleAttackGoal': ['<init>',
                                                                                                         'start',
                                                                                                         'stop',
                                                                                                         'test',
                                                                                                         'tick'],
 'entity/AnimationMonster/BossMonsters/The_Leviathan/The_Leviathan_Entity$LeviathanTentacleHoldAttackGoal': ['<init>',
                                                                                                             'start',
                                                                                                             'stop',
                                                                                                             'tick'],
 'entity/AnimationMonster/BossMonsters/The_Leviathan/The_Leviathan_Entity$LeviathanTentacleHoldBlastAttackGoal': ['<init>',
                                                                                                                  'start',
                                                                                                                  'stop',
                                                                                                                  'tick'],
 'entity/AnimationMonster/BossMonsters/The_Leviathan/The_Leviathan_Tongue_Entity': ['<init>',
                                                                                    'defineSynchedData',
                                                                                    'tick',
                                                                                    'hurtEntity',
                                                                                    'blockbreak',
                                                                                    'directMovementTowards',
                                                                                    'shouldRiderSit',
                                                                                    'addAdditionalSaveData',
                                                                                    'readAdditionalSaveData',
                                                                                    'getControllerUUID',
                                                                                    'setControllerUUID',
                                                                                    'getDuration',
                                                                                    'setDuration',
                                                                                    'getMaxDuration',
                                                                                    'setMaxDuration',
                                                                                    'getComingBack',
                                                                                    'setComingBack',
                                                                                    'getController',
                                                                                    'getTarget'],
 'init/ModEntities': ['lambda$static$11',
                      'lambda$static$52',
                      'lambda$static$54',
                      'lambda$static$60',
                      'lambda$static$64',
                      'lambda$static$70',
                      'lambda$static$71',
                      'lambda$static$74'],
 'world/data/CMWorldData': ['isLeviathanDefeatedOnce', 'setLeviathanDefeatedOnce']}
FRAGMENTS = {'entity/AnimationMonster/BossMonsters/The_Leviathan/The_Leviathan_Entity': {'<init>': [[6, 98]],
                                                                             'tick': [[4, 147],
                                                                                      [562, 686],
                                                                                      [734, 961],
                                                                                      [968, 1124]],
                                                                             'aiStep': [[71, 77],
                                                                                        [267, 484],
                                                                                        [877, 933],
                                                                                        [1080,
                                                                                         1224],
                                                                                        [1358,
                                                                                         1506],
                                                                                        [1507,
                                                                                         1530],
                                                                                        [1631,
                                                                                         1822],
                                                                                        [1889,
                                                                                         2033],
                                                                                        [2267,
                                                                                         2290],
                                                                                        [2291,
                                                                                         2768],
                                                                                        [2771,
                                                                                         2836],
                                                                                        [2974,
                                                                                         3261],
                                                                                        [3534,
                                                                                         3571]],
                                                                             '<clinit>': [[0, 49],
                                                                                          [60, 132],
                                                                                          [144,
                                                                                           158]]},
 'entity/AnimationMonster/BossMonsters/The_Leviathan/Abyss_Orb_Entity': {'tick': [[0, 147],
                                                                                  [216, 219],
                                                                                  [361, 805]]},
 'entity/AnimationMonster/BossMonsters/The_Leviathan/Abyss_Mine_Entity': {'tick': [[0, 11],
                                                                                   [48, 55],
                                                                                   [288, 432]]},
 'entity/AnimationMonster/BossMonsters/The_Leviathan/Dimensional_Rift_Entity': {'tick': [[0, 1],
                                                                                         [56, 382],
                                                                                         [444, 463],
                                                                                         [511, 562],
                                                                                         [590,
                                                                                          632]]},
 'entity/AnimationMonster/BossMonsters/The_Leviathan/Abyss_Portal_Entity': {'tick': [[0, 26],
                                                                                     [267, 552]]},
 'entity/AnimationMonster/BossMonsters/The_Leviathan/Abyss_Blast_Portal_Entity': {'tick': [[0, 1],
                                                                                           [38, 45],
                                                                                           [109,
                                                                                            329]]},
 'init/ModEntities': {'<clinit>': [[199, 213],
                                   [896, 910],
                                   [930, 944],
                                   [1032, 1046],
                                   [1100, 1114],
                                   [1202, 1233],
                                   [1270, 1284]]}}
RESOURCES = {'terrain-tag': 'data/cataclysm/tags/block/leviathan_immune.json'}

def specification():
    rows = [dict(id='cataclysm:leviathan-offense:' + n, mod_key='cataclysm',
        entry=PKG + n + '.class', methods=methods,
        **({'method_fragments': FRAGMENTS[n]} if n in FRAGMENTS else {}))
        for n, methods in sorted(METHODS.items())]
    rows.extend(dict(id='cataclysm:leviathan-offense:' + k,
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
    witnesses, classes = [], {}
    with zipfile.ZipFile(jar_path) as jar:
        for spec in specification()['evidence_specifications']:
            raw = jar.read(spec['entry'])
            row = dict(id=spec['id'], mod_key='cataclysm',
                jar_sha256=target['sha256'], entry=spec['entry'],
                entry_sha256=hashlib.sha256(raw).hexdigest())
            if spec['entry'].endswith('.class'):
                c = ClassFile(raw)
                classes[spec['entry']]=c
                row.update(class_name=c.name, superclass=c.super,
                           interfaces=c.interfaces, methods=[])
                if spec['entry'] in [PKG + n + '.class' for n in [L] + [FAMILY + n for n in ['Abyss_Orb_Entity', 'Abyss_Mine_Entity', 'Dimensional_Rift_Entity', 'Abyss_Portal_Entity', 'Abyss_Blast_Portal_Entity', 'The_Leviathan_Tongue_Entity', 'Abyss_Blast_Entity', 'Portal_Abyss_Blast_Entity']]]:
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
    helper_checks = []
    for owner, name in [(L, 'chargeDamage'), (L, 'chargeblockbreaking'),
                        (L + '$LeviathanAbyssBlastPortalAttackGoal', 'spawnUpperPortal'),
                        (FAMILY + 'The_Leviathan_Tongue_Entity', 'shouldDropItem')]:
        c = classes[PKG + owner + '.class']
        method = next(m for m in c.methods if m['name'] == name)
        target = PKG + owner + '.' + name + method['descriptor']
        callers = sorted({entry + ':' + m['name'] + m['descriptor']
            for entry, other in classes.items() if entry.startswith(PKG + FAMILY)
            for m in other.methods for i in other.instructions(m.get('code', b''))
            if i['operand'] == target})
        helper_checks.append(dict(entry=PKG + owner + '.class', method=name,
            descriptor=method['descriptor'], access=method['access'], callers_within_owned_family=callers))
    return dict(schema='tno.external_effects.native_evidence.v1', baseline=BASELINE,
        status='STATIC_EVIDENCE', witnesses=witnesses,
        scoped_private_helper_checks=helper_checks,
        note='Missing Leviathan offensive goals, delivery/control/terrain/death fragments, eight owned payload lifecycles, exact registration and terrain tag only. Locked admission/shared/status/beam ticks/native comparisons/non-damage debris reused. Visual bodies excluded; incidental visual callsites retained only for combat ordering. No runtime, Stage or whole-mod completeness claim.')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('jar', type=Path, help='Exact pinned Cataclysm 3.27 JAR')
    evidence = collect(parser.parse_args().jar)
    write_json(SPEC_FILE, specification())
    write_json(EVIDENCE_FILE, evidence)
    print(f'Leviathan offense: {len(evidence["witnesses"])} scoped witnesses captured')
