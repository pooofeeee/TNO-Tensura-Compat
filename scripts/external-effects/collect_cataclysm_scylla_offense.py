"""Bounded R2k10b Scylla offense/payload witnesses from the pinned JAR.

Admission/state and status payload methods already captured remain cold, locked
references. Only the finite offensive entries and missing combat fragments.
"""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

from catalog_common import BASELINE, OUT, read_json, write_json
from classfile import ClassFile, Reader

PKG = 'com/github/L_Ender/cataclysm/'
FAMILY = 'entity/InternalAnimationMonster/IABossMonsters/Scylla/'
S = FAMILY + 'Scylla_Entity'
ANCHOR = FAMILY + 'Scylla_Ceraunus_Entity'
STORM = 'entity/effect/Lightning_Storm_Entity'
AREA = 'entity/effect/Lightning_Area_Effect_Entity'
WAVE = 'entity/effect/Wave_Entity'
BASE_SPEAR = 'entity/projectile/Elemental_Spear_Entity'
WATER_SPEAR = 'entity/projectile/Water_Spear_Entity'
LIGHTNING_SPEAR = 'entity/projectile/Lightning_Spear_Entity'
SPARK = 'entity/projectile/Spark_Entity'
SERPENT = 'entity/projectile/Storm_Serpent_Entity'
REGISTRY = 'init/ModEntities'
SPEC_FILE = OUT / 'native-specifications/cataclysm-scylla-offense.json'
EVIDENCE_FILE = OUT / 'native-evidence/cataclysm-scylla-offense.json'
GOALS = ['1',
 '4',
 '5',
 '6',
 '7',
 'AnchorThrowGoal',
 'Back_StepGoal',
 'HorizontalSwingGoal',
 'Scylla_Flying',
 'Scylla_Lightning_Explosion',
 'ScyllafallingState',
 'SpearThrowGoal',
 'SummonSnake',
 'ThunderCloud',
 'WhipAndSpearGoal']
METHODS = {'entity/InternalAnimationMonster/IABossMonsters/Scylla/Scylla_Ceraunus_Entity': ['<init>',
                                                                                  'defineSynchedData',
                                                                                  'getControllerUUID',
                                                                                  'setControllerUUID',
                                                                                  'getController',
                                                                                  'getGrab',
                                                                                  'setGrab',
                                                                                  'getHookMode',
                                                                                  'setHookMode',
                                                                                  'getYrotOld',
                                                                                  'setYrotOld',
                                                                                  'getXrotOld',
                                                                                  'setXrotOld',
                                                                                  'getPhase',
                                                                                  'setPhase',
                                                                                  'addAdditionalSaveData',
                                                                                  'readAdditionalSaveData',
                                                                                  'tick',
                                                                                  'isAcceptibleReturnOwner',
                                                                                  'onHitEntity',
                                                                                  'doKnockback',
                                                                                  'onHit',
                                                                                  'shouldRiderSit',
                                                                                  'getWaterInertia',
                                                                                  'canUsePortal',
                                                                                  'getDefaultGravity'],
 'entity/InternalAnimationMonster/IABossMonsters/Scylla/Scylla_Entity': ['blockbreak',
                                                                         'AreaAttack',
                                                                         'SpinDamage',
                                                                         'Stormknockback',
                                                                         'spawnLightning',
                                                                         'floatScylla',
                                                                         'launch',
                                                                         'isAlliedTo',
                                                                         'die',
                                                                         'AfterDefeatBoss',
                                                                         'deathtimer',
                                                                         'canRide'],
 'entity/InternalAnimationMonster/IABossMonsters/Scylla/Scylla_Entity$1': ['<init>', 'canUse'],
 'entity/InternalAnimationMonster/IABossMonsters/Scylla/Scylla_Entity$4': ['<init>', 'stop'],
 'entity/InternalAnimationMonster/IABossMonsters/Scylla/Scylla_Entity$5': ['<init>',
                                                                           'canUse',
                                                                           'start',
                                                                           'stop',
                                                                           'tick'],
 'entity/InternalAnimationMonster/IABossMonsters/Scylla/Scylla_Entity$6': ['<init>',
                                                                           'canUse',
                                                                           'start',
                                                                           'stop'],
 'entity/InternalAnimationMonster/IABossMonsters/Scylla/Scylla_Entity$7': ['<init>',
                                                                           'canUse',
                                                                           'start',
                                                                           'stop'],
 'entity/InternalAnimationMonster/IABossMonsters/Scylla/Scylla_Entity$AnchorThrowGoal': ['<init>',
                                                                                         'canUse',
                                                                                         'start',
                                                                                         'stop',
                                                                                         'tick'],
 'entity/InternalAnimationMonster/IABossMonsters/Scylla/Scylla_Entity$Back_StepGoal': ['<init>',
                                                                                       'canUse',
                                                                                       'start',
                                                                                       'stop'],
 'entity/InternalAnimationMonster/IABossMonsters/Scylla/Scylla_Entity$HorizontalSwingGoal': ['<init>',
                                                                                             'canContinueToUse',
                                                                                             'canUse',
                                                                                             'isInterruptable',
                                                                                             'requiresUpdateEveryTick',
                                                                                             'start'],
 'entity/InternalAnimationMonster/IABossMonsters/Scylla/Scylla_Entity$Scylla_Flying': ['<init>',
                                                                                       'canUse',
                                                                                       'start',
                                                                                       'stop',
                                                                                       'tick'],
 'entity/InternalAnimationMonster/IABossMonsters/Scylla/Scylla_Entity$Scylla_Lightning_Explosion': ['<init>',
                                                                                                    'canUse',
                                                                                                    'start',
                                                                                                    'stop',
                                                                                                    'tick'],
 'entity/InternalAnimationMonster/IABossMonsters/Scylla/Scylla_Entity$ScyllafallingState': ['<init>',
                                                                                            'canContinueToUse',
                                                                                            'start',
                                                                                            'stop',
                                                                                            'tick'],
 'entity/InternalAnimationMonster/IABossMonsters/Scylla/Scylla_Entity$SpearThrowGoal': ['<init>',
                                                                                        'canContinueToUse',
                                                                                        'canUse',
                                                                                        'isInterruptable',
                                                                                        'requiresUpdateEveryTick',
                                                                                        'start',
                                                                                        'stop',
                                                                                        'tick'],
 'entity/InternalAnimationMonster/IABossMonsters/Scylla/Scylla_Entity$SummonSnake': ['<init>',
                                                                                     'canUse',
                                                                                     'start',
                                                                                     'stop',
                                                                                     'tick'],
 'entity/InternalAnimationMonster/IABossMonsters/Scylla/Scylla_Entity$ThunderCloud': ['<init>',
                                                                                      'canUse',
                                                                                      'start',
                                                                                      'stop',
                                                                                      'tick'],
 'entity/InternalAnimationMonster/IABossMonsters/Scylla/Scylla_Entity$WhipAndSpearGoal': ['<init>',
                                                                                          'canUse',
                                                                                          'start',
                                                                                          'stop',
                                                                                          'tick'],
 'entity/effect/Lightning_Area_Effect_Entity': ['<init>',
                                                'defineSynchedData',
                                                'setRadius',
                                                'getRadius',
                                                'setDamage',
                                                'getDamage',
                                                'setWaiting',
                                                'isWaiting',
                                                'getDuration',
                                                'setDuration',
                                                'damage',
                                                'getRadiusOnUse',
                                                'setRadiusOnUse',
                                                'getRadiusPerTick',
                                                'setRadiusPerTick',
                                                'getDurationOnUse',
                                                'setDurationOnUse',
                                                'getWaitTime',
                                                'setWaitTime',
                                                'setOwner',
                                                'getOwner',
                                                'readAdditionalSaveData',
                                                'addAdditionalSaveData',
                                                'getDimensions',
                                                'refreshDimensions',
                                                'onSyncedDataUpdated'],
 'entity/effect/Lightning_Storm_Entity': ['<init>',
                                          'defineSynchedData',
                                          'getLifespan',
                                          'setLifespan',
                                          'getDelay',
                                          'setDelay',
                                          'getSize',
                                          'setSize',
                                          'setCaster',
                                          'getCaster',
                                          'getDamage',
                                          'setDamage',
                                          'getHpDamage',
                                          'setHpDamage',
                                          'getDimensions',
                                          'damageEntityLivingBaseNearby',
                                          'damage',
                                          'addAdditionalSaveData',
                                          'readAdditionalSaveData',
                                          'onSyncedDataUpdated',
                                          'refreshDimensions'],
 'entity/effect/Wave_Entity': ['<init>',
                               'maxUpStep',
                               'setOwner',
                               'getOwner',
                               'defineSynchedData',
                               'getState',
                               'setState',
                               'getDamage',
                               'setDamage',
                               'getYRot',
                               'setYRot',
                               'getLifespan',
                               'setLifespan',
                               'getMaxTicks',
                               'setMaxTicks',
                               'readAdditionalSaveData',
                               'addAdditionalSaveData',
                               'lerpTo',
                               'lerpMotion'],
 'entity/projectile/Elemental_Spear_Entity': ['<init>',
                                              'defineSynchedData',
                                              'getState',
                                              'setState',
                                              'getDamage',
                                              'setDamage',
                                              'getClipType',
                                              'tick',
                                              'onHitEntity',
                                              'onHit',
                                              'canHitEntity',
                                              'getInertia',
                                              'addAdditionalSaveData',
                                              'readAdditionalSaveData',
                                              'isPickable',
                                              'hurt',
                                              'checkDespawn',
                                              'removeWhenFarAway',
                                              'assignDirectionalMovement',
                                              'onDeflection'],
 'entity/projectile/Lightning_Spear_Entity': ['<init>',
                                              'defineSynchedData',
                                              'getAreaRadius',
                                              'setAreaRadius',
                                              'getAreaDamage',
                                              'setAreaDamage',
                                              'getHpDamage',
                                              'setHpDamage',
                                              'onHitEntity',
                                              'onHitBlock',
                                              'getInertia',
                                              'addAdditionalSaveData',
                                              'readAdditionalSaveData'],
 'entity/projectile/Spark_Entity': ['<init>',
                                    'defineSynchedData',
                                    'getDamage',
                                    'setDamage',
                                    'getAreaRadius',
                                    'setAreaRadius',
                                    'getAreaDamage',
                                    'setAreaDamage',
                                    'getHpDamage',
                                    'setHpDamage',
                                    'addAdditionalSaveData',
                                    'readAdditionalSaveData',
                                    'onHitEntity',
                                    'onHitBlock',
                                    'spawnArea',
                                    'onHit',
                                    'getDefaultGravity'],
 'entity/projectile/Storm_Serpent_Entity': ['<init>',
                                            'defineSynchedData',
                                            'getState',
                                            'setState',
                                            'getRight',
                                            'setRight',
                                            'getDamage',
                                            'setDamage',
                                            'getCaster',
                                            'setCaster',
                                            'readAdditionalSaveData',
                                            'addAdditionalSaveData',
                                            'lookAt',
                                            'rotlerp'],
 'entity/projectile/Water_Spear_Entity': ['<init>',
                                          'defineSynchedData',
                                          'getTotalBounces',
                                          'setTotalBounces',
                                          'onHitBlock',
                                          'getInertia',
                                          'addAdditionalSaveData',
                                          'readAdditionalSaveData'],
 'init/ModEntities': ['lambda$static$7',
                      'lambda$static$37',
                      'lambda$static$44',
                      'lambda$static$47',
                      'lambda$static$48',
                      'lambda$static$67',
                      'lambda$static$101',
                      'lambda$static$102']}
FRAGMENTS = {'entity/InternalAnimationMonster/IABossMonsters/Scylla/Scylla_Ceraunus_Entity': {'onHitBlock': [[0, 56], [124, 310]]},
 'entity/InternalAnimationMonster/IABossMonsters/Scylla/Scylla_Entity': {'SummonWave': [[0, 202]],
                                                                         'aiStep': [[0, 118],
                                                                                    [159, 221],
                                                                                    [262, 326],
                                                                                    [367, 423],
                                                                                    [464, 525],
                                                                                    [566, 572],
                                                                                    [626, 701],
                                                                                    [801, 815],
                                                                                    [869, 944],
                                                                                    [1044, 1050],
                                                                                    [1314, 1338],
                                                                                    [1378, 1385],
                                                                                    [1507, 1682],
                                                                                    [1792, 1888],
                                                                                    [2675, 2681],
                                                                                    [2754, 2865],
                                                                                    [2886, 2937],
                                                                                    [3089, 3133],
                                                                                    [3188, 3629],
                                                                                    [4059, 4065],
                                                                                    [4231, 4237],
                                                                                    [4300, 4305],
                                                                                    [4438, 4559],
                                                                                    [4645, 4652],
                                                                                    [4754, 4989],
                                                                                    [4992, 4999],
                                                                                    [5287, 5429],
                                                                                    [5551, 5557],
                                                                                    [6100, 6215],
                                                                                    [6218, 6224],
                                                                                    [6907, 7022],
                                                                                    [7025, 7431],
                                                                                    [7803, 7923],
                                                                                    [7926, 7933],
                                                                                    [8221, 8363],
                                                                                    [8485, 8491],
                                                                                    [8545, 8570],
                                                                                    [8868, 9000],
                                                                                    [9943, 9958],
                                                                                    [10012, 10087]],
                                                                         'registerGoals': [[57,
                                                                                            111],
                                                                                           [164,
                                                                                            298],
                                                                                           [351,
                                                                                            695]],
                                                                         'tick': [[67, 106],
                                                                                  [147, 290],
                                                                                  [310, 355]]},
 'entity/InternalAnimationMonster/IABossMonsters/Scylla/Scylla_Entity$HorizontalSwingGoal': {'tick': [[0,
                                                                                                       943]]},
 'entity/effect/Lightning_Area_Effect_Entity': {'tick': [[0, 21], [240, 386]]},
 'entity/effect/Lightning_Storm_Entity': {'tick': [[0, 31], [239, 280]]},
 'entity/effect/Wave_Entity': {'tick': [[0, 203], [481, 569]]},
 'entity/projectile/Spark_Entity': {'tick': [[0, 1]]},
 'entity/projectile/Storm_Serpent_Entity': {'tick': [[0, 11], [847, 1222]]},
 'init/ModEntities': {'<clinit>': [[131, 145],
                                   [641, 655],
                                   [760, 774],
                                   [811, 842],
                                   [1151, 1165],
                                   [1729, 1760]]}}
RESOURCES = {'terrain-tag': 'data/cataclysm/tags/block/scylla_immune.json'}

def specification():
    rows = [dict(id='cataclysm:scylla-offense:' + n, mod_key='cataclysm',
        entry=PKG + n + '.class', methods=methods,
        **({'method_fragments': FRAGMENTS[n]} if n in FRAGMENTS else {}))
        for n, methods in sorted(METHODS.items())]
    rows.extend(dict(id='cataclysm:scylla-offense:' + k,
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
    witnesses, classes = [], {}
    with zipfile.ZipFile(jar_path) as jar:
        for spec in specification()['evidence_specifications']:
            raw = jar.read(spec['entry'])
            row = dict(id=spec['id'], mod_key='cataclysm', jar_sha256=target['sha256'],
                entry=spec['entry'], entry_sha256=hashlib.sha256(raw).hexdigest())
            if spec['entry'].endswith('.class'):
                c = ClassFile(raw)
                classes[spec['entry']] = c
                row.update(class_name=c.name, superclass=c.super,
                           interfaces=c.interfaces, methods=[])
                if spec['entry'] in {PKG + n + '.class' for n in
                        [S, ANCHOR, STORM, AREA, WAVE, BASE_SPEAR,
                         WATER_SPEAR, LIGHTNING_SPEAR, SPARK, SERPENT]}:
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
    private_checks = []
    root_class = classes[PKG + S + '.class']
    for name in ['Whip', 'LightningAttack', 'StrikeWindmillLightning', 'WhipLightningAttack']:
        method = next(m for m in root_class.methods if m['name'] == name)
        target = PKG + S + '.' + name + method['descriptor']
        callers = sorted({entry + ':' + m['name'] + m['descriptor']
            for entry, c in classes.items() if entry != PKG + REGISTRY + '.class'
            for m in c.methods for i in c.instructions(m.get('code', b''))
            if i['operand'] == target})
        private_checks.append(dict(entry=PKG + S + '.class', method=name,
            descriptor=method['descriptor'], access=method['access'],
            callers_within_owned_family=callers))
    return dict(schema='tno.external_effects.native_evidence.v1', baseline=BASELINE,
        status='STATIC_EVIDENCE', witnesses=witnesses, scoped_private_helper_checks=private_checks,
        note='Bounded Scylla offense selection/goals, direct damage/control, eight owned payload entries plus shared spear base, terrain tag and exact registry only. Previously captured admission/status/team/native contracts reused without regeneration. Visual-only bodies omitted; incidental visual callsites retained only for combat ordering. Uncalled private helper chains not promoted to active mechanics. Static only; no Stage or whole-mod completeness claim.')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('jar', type=Path, help='Exact pinned Cataclysm 3.27 JAR')
    evidence = collect(parser.parse_args().jar)
    write_json(SPEC_FILE, specification())
    write_json(EVIDENCE_FILE, evidence)
    print(f'Scylla offense: {len(evidence["witnesses"])} scoped witnesses captured')
