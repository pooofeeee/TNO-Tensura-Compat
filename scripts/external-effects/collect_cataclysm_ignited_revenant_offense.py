"""Capture only new R2k12b Ignited Revenant offense/owned-payload witnesses.

Reuse protected admission/goal setup and shared animation, pursuit, team-tag,
damage and lifecycle contracts. Exclude sounds, particles and old tick offsets.
"""
import argparse
import hashlib
from pathlib import Path
import struct
import zipfile

from catalog_common import BASELINE, OUT, read_json, write_json
from classfile import ClassFile
from collect_cataclysm_ender_golem_offense import instructions as native_instructions

PKG = 'com/github/L_Ender/cataclysm/'
R = 'entity/AnimationMonster/BossMonsters/Ignited_Revenant_Entity'
ASH = 'entity/projectile/Ashen_Breath_Entity'
BONE = 'entity/projectile/Blazing_Bone_Entity'
REGISTRY = 'init/ModEntities'
SPEC_FILE = OUT / 'native-specifications/cataclysm-ignited-revenant-offense.json'
EVIDENCE_FILE = OUT / 'native-evidence/cataclysm-ignited-revenant-offense.json'
METHODS = {
    R: ['getAnimations', 'isAlliedTo', 'onDeathAIUpdate', 'repelEntities',
        'access$000', 'access$100', 'access$200', 'access$300', 'access$400'],
    R + '$ShootGoal': [],
    R + '$BoneStormGoal': ['<init>', 'tick'],
    ASH: ['<init>', 'getPistonPushReaction', 'hitEntities', 'defineSynchedData',
        'getDamage', 'setDamage', 'setCaster', 'getCaster',
        'readAdditionalSaveData', 'addAdditionalSaveData', 'isPickable', 'push',
        'canBeCollidedWith', 'getEntityLivingBaseNearby', 'getEntitiesNearby',
        'isPushable', 'lambda$getEntitiesNearby$0', '<clinit>'],
    BONE: ['<init>', 'defineSynchedData', 'getDamage', 'setDamage',
        'addAdditionalSaveData', 'readAdditionalSaveData', 'onHitEntity',
        'isNoGravity', 'onHit', '<clinit>'],
    REGISTRY: [],
}
FRAGMENTS = {
    R: {'tick': [[106, 560]], 'registerGoals': [[16, 33]], '<clinit>': [[0, 13]],
        'launchbone1': [[11, 180]], 'launchbone2': [[11, 181]], 'launchbone3': [[11, 181]]},
    R + '$ShootGoal': {'tick': [[0, 54], [87, 266]]},
    ASH: {'tick': [[0, 43], [510, 542]]},
    REGISTRY: {'<clinit>': [[590, 604], [845, 859]]},
}


def instructions(c, code):
    result = native_instructions(c, code)
    for i in result:
        if i['opcode']=='0xaa':
            pos = (i['offset'] + 4) & ~3
            default, low, high = struct.unpack_from('>iii', code, pos)
            i['switch_default_target'] = i['offset'] + default
            i['switch_cases'] = {str(k): i['offset'] + struct.unpack_from('>i', code,
                pos + 12 + 4 * (k - low))[0] for k in range(low, high + 1)}
    return result


def specification():
    return dict(schema='tno.external_effects.native_specification.v1', baseline=BASELINE,
        evidence_specifications=[dict(id='cataclysm:ignited-revenant-offense:' + n,
            mod_key='cataclysm', entry=PKG + n + '.class', methods=methods,
            method_fragments=FRAGMENTS.get(n, {})) for n, methods in sorted(METHODS.items())])


def collect(jar_path):
    target = next(t for t in read_json(OUT / 'jar-inventory.json')['targets'] if t['key']=='cataclysm')
    jar_path = Path(jar_path)
    with jar_path.open('rb') as stream:
        assert hashlib.file_digest(stream, 'sha256').hexdigest()==target['sha256']
    assert jar_path.stat().st_size==target['size_bytes']
    witnesses = []
    with zipfile.ZipFile(jar_path) as jar:
        for spec in specification()['evidence_specifications']:
            raw = jar.read(spec['entry'])
            c = ClassFile(raw)
            row = dict(id=spec['id'], mod_key='cataclysm', jar_sha256=target['sha256'],
                entry=spec['entry'], entry_sha256=hashlib.sha256(raw).hexdigest(),
                class_name=c.name, superclass=c.super, interfaces=c.interfaces, methods=[])
            if spec['entry'] in {PKG+ASH+'.class', PKG+BONE+'.class'}:
                row['declared_method_names'] = sorted({m['name'] for m in c.methods})
            for name in spec['methods'] + list(spec['method_fragments']):
                matches = [m for m in c.methods if m['name']==name]
                assert matches, (spec['entry'], name)
                for m in matches:
                    code = m.get('code', b'')
                    ins = instructions(c, code)
                    ranges = spec['method_fragments'].get(name)
                    if ranges:
                        ins = [i for i in ins if any(a<=i['offset']<=b for a,b in ranges)]
                        assert all(any(i['offset']==v for i in ins) for span in ranges for v in span)
                    row['methods'].append(dict(name=name, descriptor=m['descriptor'],
                        code_sha256=hashlib.sha256(code).hexdigest(), instructions=ins,
                        **({'instruction_offset_ranges': ranges} if ranges else {})))
            witnesses.append(row)
    return dict(schema='tno.external_effects.native_evidence.v1', baseline=BASELINE,
        status='STATIC_EVIDENCE', witnesses=witnesses,
        note='Five exact Revenant/goal/owned-payload classes and two exact entity-ID registrations only. Old incoming/state/goal setup '
             'and root tick0..103 excluded; no sounds, particles, equipment, unrelated bosses '
             'or recursive JAR scan. Existing pursuit/animation/team/native contracts reused '
             'without regeneration. Static only; no Stage policy or runtime tests.')


if __name__=='__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('jar', type=Path, help='Exact pinned Cataclysm 3.27 JAR')
    evidence = collect(parser.parse_args().jar)
    write_json(SPEC_FILE, specification())
    write_json(EVIDENCE_FILE, evidence)
    print(f'Ignited Revenant offense: {len(evidence["witnesses"])} scoped witnesses captured')
