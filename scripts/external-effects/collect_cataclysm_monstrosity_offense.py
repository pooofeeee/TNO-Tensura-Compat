"""Capture only missing R2k4b Monstrosity offense/payload witnesses.

Explicit pinned entries only. Existing aiStep, admission/setup, shared/status,
Guardian and native projectile/explosion contracts are immutable reused inputs.
Previously captured registration/tick fragments are excluded from new capture.
"""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

from catalog_common import BASELINE, OUT, read_json, write_json
from classfile import ClassFile, Reader
from collect_cataclysm_monstrosity_admission import M, PKG, REGISTRY

L = 'entity/projectile/Lava_Bomb_Entity'
F = 'entity/projectile/Flare_Bomb_Entity'
J = 'entity/projectile/Flame_Jet_Entity'
D = 'entity/effect/Cm_Falling_Block_Entity'
AG = 'entity/InternalAnimationMonster/AI/InternalAttackGoal'
MG = 'entity/InternalAnimationMonster/AI/InternalMoveGoal'
MC = 'entity/etc/FowardMoveController'
SPEC_FILE = OUT / 'native-specifications/cataclysm-monstrosity-offense.json'
EVIDENCE_FILE = OUT / 'native-evidence/cataclysm-monstrosity-offense.json'
METHODS = {
    M: ['EarthQuake', 'OverPowerKnockBack', 'launch', 'CircleFlameJet', 'spawnJet',
        'StompDamage', 'spawnBlocks', 'doAbsorptionEffects', 'doAbsorptionEffect',
        'ChargeBlockBreaking', 'berserkBlockBreaking', 'BlockBreaking', 'isAlliedTo'],
    M + '$1': ['<init>', 'canUse'],
    M + '$2': ['<init>', 'canUse'],
    M + '$4': ['<init>', 'canUse'],
    M + '$5': ['<init>', 'canUse', 'stop'],
    M + '$Magmashoot': ['<init>', 'canUse', 'start', 'stop', 'tick', 'requiresUpdateEveryTick'],
    M + '$Flareshoot': ['<init>', 'canUse', 'start', 'stop', 'tick', 'requiresUpdateEveryTick'],
    M + '$ShoulderCheck': ['<init>', 'canUse', 'start', 'stop', 'tick', 'requiresUpdateEveryTick'],
    AG: ['<init>', 'canUse', 'isInterruptable', 'start', 'stop', 'EndState', 'canContinueToUse',
         'tick', 'requiresUpdateEveryTick'],
    MG: ['<init>', 'canUse', 'stop', 'canContinueToUse', 'start', 'tick', 'requiresUpdateEveryTick'],
    MC: ['forward', 'ForwardMoveControl', 'isWalkableForward'],
    L: ['<init>', 'defineSynchedData', 'onHit', 'onHitEntity', 'onHitBlock', 'doTerrainEffects',
        'tick', 'remove', 'applyGravity', 'setLavaPos', 'getLavaPos', 'getGround', 'setGround',
        'getLavaTime', 'setLavaTime', 'getMaxLavaTime', 'setMaxLavaTime',
        'readAdditionalSaveData', 'addAdditionalSaveData', 'getDefaultGravity'],
    F: ['<init>', 'onHitEntity', 'onHit', 'PlusStrikeRune', 'XStrikeRune', 'spawnJet', 'getDefaultGravity'],
    J: ['<init>', 'defineSynchedData', 'getDamage', 'setDamage', 'setCaster', 'getCaster',
        'readAdditionalSaveData', 'addAdditionalSaveData', 'tick', 'damage'],
    # This exact spawned entity is NOT vanilla FallingBlockEntity: inspect only
    # enough to exclude a second damage/placement payload and retain lifecycle.
    D: ['<init>', 'tick', 'addAdditionalSaveData', 'readAdditionalSaveData'],
    REGISTRY: ['lambda$static$4', 'lambda$static$5', 'lambda$static$6', 'lambda$static$40'],
}
FRAGMENTS = {
    M: {'registerGoals': [[58, 177], [240, 385]], 'tick': [[198, 291]]},
    MC: {'tick': [[198, 224]]},  # only FORWARD dispatch, not unrelated controller operations
    F: {'tick': [[0, 1], [37, 61]]},  # native tick and combat pattern yaw, excluding trail data
    REGISTRY: {'<clinit>': [[80, 128], [692, 706]]},
}
DESCRIPTORS = {AG: {'<init>': '(L' + PKG +
    'entity/InternalAnimationMonster/Internal_Animation_Monster;IIIIIF)V'}}
RESOURCES = {'team-tag': 'data/cataclysm/tags/entity_type/team_monstrosity.json',
             'immune-tag': 'data/cataclysm/tags/block/netherite_monstrosity_immune.json'}


def specification():
    rows = [dict(id='cataclysm:monstrosity-offense:' + name, mod_key='cataclysm',
        entry=PKG + name + '.class', methods=names,
        **({'method_fragments': FRAGMENTS[name]} if name in FRAGMENTS else {}),
        **({'method_descriptors': DESCRIPTORS[name]} if name in DESCRIPTORS else {}))
        for name, names in sorted(METHODS.items())]
    rows.extend(dict(id='cataclysm:monstrosity-offense:' + k, mod_key='cataclysm', entry=v)
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
                if spec['entry'] in [PKG + n + '.class' for n in [L, F, J, D]]:
                    row['declared_method_names'] = sorted({m['name'] for m in c.methods})
                    row['declared_fields'] = [dict(name=f['name'], descriptor=f['descriptor']) for f in c.fields]
                for name in spec['methods'] + list(spec.get('method_fragments', {})):
                    descriptor = spec.get('method_descriptors', {}).get(name)
                    matches = [m for m in c.methods if m['name'] == name
                               and (descriptor is None or m['descriptor'] == descriptor)]
                    assert matches, (spec['entry'], name)
                    for m in matches:
                        code = m.get('code', b'')
                        ins = list(c.instructions(code))
                        ranges = spec.get('method_fragments', {}).get(name)
                        if ranges:
                            ins = [i for i in ins if any(a <= i['offset'] <= b for a, b in ranges)]
                            assert all(any(i['offset'] == v for i in ins) for r in ranges for v in r)
                        row['methods'].append(dict(name=name, descriptor=m['descriptor'],
                            code_sha256=hashlib.sha256(code).hexdigest(), instructions=ins,
                            **({'instruction_offset_ranges': ranges} if ranges else {})))
                if spec['entry'] == PKG + REGISTRY + '.class':
                    r = Reader(next(raw for name, raw in c.attributes if name == 'BootstrapMethods'))
                    bs = [(r.u2(), [r.u2() for _ in range(r.u2())]) for _ in range(r.u2())]
                    row['registration_bootstraps'] = [dict(index=i, handle=c.resolve(bs[i][0]),
                        arguments=[c.resolve(a) for a in bs[i][1]]) for i in [73, 107, 108, 109, 118, 119, 120, 154]]
            else:
                row['data'] = json.loads(raw)
            witnesses.append(row)
    return dict(schema='tno.external_effects.native_evidence.v1', baseline=BASELINE,
        status='STATIC_EVIDENCE', witnesses=witnesses,
        note='Missing Monstrosity offense/owned payload methods only. Reused aiStep/shared/status/'
             'admission/native witnesses are not regenerated. No runtime, Stage or whole-mod completeness claim.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('jar', type=Path, help='Exact pinned Cataclysm 3.27 JAR')
    evidence = collect(parser.parse_args().jar)
    write_json(SPEC_FILE, specification())
    write_json(EVIDENCE_FILE, evidence)
    print(f'Monstrosity offense: {len(evidence["witnesses"])} scoped witnesses captured')
