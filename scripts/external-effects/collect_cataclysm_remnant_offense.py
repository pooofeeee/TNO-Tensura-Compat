"""Missing R2k7b Ancient Remnant offense witnesses from the exact pinned JAR.

Explicit entries/methods/fragments only. Admission, shared/status, prior bosses,
native projectile comparisons and non-damage debris are reused, not recaptured.
"""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

from catalog_common import BASELINE, OUT, read_json, write_json
from classfile import ClassFile, Reader
from collect_cataclysm_remnant_admission import AM, PKG, R, REGISTRY

S = 'entity/effect/Sandstorm_Entity'
E = 'entity/projectile/EarthQuake_Entity'
T = 'entity/projectile/Ancient_Desert_Stele_Entity'
SPEC_FILE = OUT / 'native-specifications/cataclysm-remnant-offense.json'
EVIDENCE_FILE = OUT / 'native-evidence/cataclysm-remnant-offense.json'
METHODS = {
    R: ['Charge', 'ChargeBlockBreaking', 'StompDamage', 'spawnBlocks',
        'getTailEntityLivingBaseNearby', 'getTailEntitiesNearby',
        'lambda$getTailEntitiesNearby$0', 'EarthQuakeSummon', 'isAlliedTo',
        'floatRemnant', 'canStandOnFluid', 'isPushedByFluid', 'travel',
        'canBePushedByEntity', 'repelEntities', 'die', 'deathtimer',
        'onDeathAIUpdate', 'AfterDefeatBoss',
        'access$000', 'access$100', 'access$200', 'access$300', 'access$400', 'access$500'],
    R + '$AttackMode': ['<clinit>'],
    R + '$RemnantAttackModeGoal': ['<init>', 'canUse', 'canContinueToUse',
        'start', 'stop', 'tick', 'requiresUpdateEveryTick'],
    R + '$RemnantAttackGoal': ['<init>', 'canUse', 'start', 'stop'],
    R + '$RemnantChargeGoal': ['<init>', 'canUse', 'start', 'tick', 'stop'],
    R + '$RemnantStompGoal': ['<init>', 'canUse', 'start', 'stop', 'tick',
        'canContinueToUse', 'isInterruptable', 'requiresUpdateEveryTick'],
    R + '$RemnantMonolithAttackGoal': ['<init>', 'canUse', 'start', 'stop', 'tick',
        'StrikeWindmillMonolith', 'spawnSpikeLine'],
    R + '$1': ['<init>', 'canUse', 'stop'],
    R + '$2': ['<init>', 'canContinueToUse', 'stop', 'tick'],
    R + '$3': ['<init>', 'canUse', 'stop'],
    R + '$4': ['<init>', 'canUse'],
    AM: ['circleEntity'],
    S: ['<init>', 'defineSynchedData', 'getLifespan', 'setLifespan',
        'getOffset', 'setOffset', 'setCaster', 'getCaster', 'getState', 'setState',
        'updateMotion', 'addAdditionalSaveData', 'readAdditionalSaveData'],
    E: ['<init>', 'tick', 'shoot', 'shootFromRotation', 'defineSynchedData',
        'getDamage', 'setDamage', 'strongKnockback', 'canCollideWith',
        'canBeCollidedWith', 'canHitEntity', 'isOnFire', 'maxUpStep'],
    T: ['<init>', 'tick', 'defineSynchedData', 'getDamage', 'setDamage',
        'getWarmUp', 'setWarmUp', 'isActivate', 'setActivate', 'getCaster',
        'setCaster', 'onHitBlock', 'lambda$tick$0',
        'addAdditionalSaveData', 'readAdditionalSaveData'],
    REGISTRY: ['lambda$static$76', 'lambda$static$83', 'lambda$static$86',
        'buildPredicateFromTag', 'lambda$buildPredicateFromTag$103'],
}
FRAGMENTS = {
    R: {'registerGoals': [[0, 186], [251, 490]],
        'tick': [[100, 233], [258, 259]],
        # Exclude locked POWER phase and the purely visual preparation/recovery/roar.
        'aiStep': [[4, 86], [383, 491], [980, 2673], [2903, 2935], [3086, 6932]]},
    S: {'tick': [[0, 25], [432, 502], [512, 519]]},
    E: {'onUpdateInAir': [[0, 208]]},
    T: {'onHit': [[0, 2], [50, 57], [134, 138]]},
    REGISTRY: {'<clinit>': [[1304, 1318], [1423, 1437], [1474, 1488]]},
}
RESOURCES = {
    'target-tag': 'data/cataclysm/tags/entity_type/ancient_remnant_target.json',
    'team-tag': 'data/cataclysm/tags/entity_type/team_ancient_remnant.json',
    'terrain-tag': 'data/cataclysm/tags/block/remnant_immune.json',
}


def specification():
    rows = [dict(id='cataclysm:remnant-offense:' + n, mod_key='cataclysm',
        entry=PKG + n + '.class', methods=methods,
        **({'method_fragments': FRAGMENTS[n]} if n in FRAGMENTS else {}))
        for n, methods in sorted(METHODS.items())]
    rows.extend(dict(id='cataclysm:remnant-offense:' + k, mod_key='cataclysm', entry=v)
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
                if spec['entry'] in [PKG + n + '.class' for n in [R, S, E, T]]:
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
                            assert all(any(i['offset'] == v for i in ins) for r in ranges for v in r), (spec['entry'], name, ranges)
                        row['methods'].append(dict(name=name, descriptor=m['descriptor'],
                            code_sha256=hashlib.sha256(code).hexdigest(), instructions=ins,
                            **({'instruction_offset_ranges': ranges} if ranges else {})))
                if spec['entry'] == PKG + REGISTRY + '.class':
                    r = Reader(next(data for n, data in c.attributes if n == 'BootstrapMethods'))
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
        note='Missing Ancient Remnant offensive goals, offense/state/terrain/death fragments '
             'and three directly owned payloads only. AreaAttack/TailAreaAttack, Sandstorm.damage, '
             'stele.onHitEntity, debris, admission/shared/status/prior bosses and native comparisons '
             'are reused. No runtime, Stage or whole-mod completeness claim.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('jar', type=Path, help='Exact pinned Cataclysm 3.27 JAR')
    evidence = collect(parser.parse_args().jar)
    write_json(SPEC_FILE, specification())
    write_json(EVIDENCE_FILE, evidence)
    print(f'Remnant offense: {len(evidence["witnesses"])} scoped witnesses captured')
