"""Missing R2k5b Ignis offense witnesses, read from the exact pinned JAR.

Explicit entries/methods only. Locked tick/aiStep, status producers, admission,
shared animation, projectile, explosion and debris witnesses are reused.
"""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

from catalog_common import BASELINE, OUT, read_json, write_json
from classfile import ClassFile, Reader
from collect_cataclysm_ignis_admission import I, PKG, REGISTRY

F = 'entity/projectile/Ignis_Fireball_Entity'
A = 'entity/projectile/Ignis_Abyss_Fireball_Entity'
P = 'entity/projectile/CMAbstractHurtingProjectile'
S = 'entity/effect/Flame_Strike_Entity'
X = 'util/CustomExplosion/IgnisExplosion'
W = 'world/data/CMWorldData'
MOVE = 'entity/AnimationMonster/AI/AttackMoveGoal'
HOLD = 'entity/AnimationMonster/AI/AttackAniamtionGoal3'
SPEC_FILE = OUT / 'native-specifications/cataclysm-ignis-offense.json'
EVIDENCE_FILE = OUT / 'native-evidence/cataclysm-ignis-offense.json'
METHODS = {
    I: ['getAnimations', 'getRandomPoke', 'getRandomReinforced', 'shouldFollowUp',
        'setTargetPosition', 'getTargetPosition', 'Poke', 'shouldRiderSit',
        'getControllingPassenger', 'ShieldSmashDamage', 'UltimateAttack',
        'ShieldExplode', 'shootFireball', 'shootAbyssFireball', 'bladeFireball',
        'spawnFlameStrike', 'isAlliedTo', 'blockbreak', 'getDeathAnimation',
        'AfterDefeatBoss', 'canBePushedByEntity', 'repelEntities', 'floatStrider',
        'canStandOnFluid', 'isAffectedByFluids', 'isPushedByFluid'],
    I + '$1': ['<init>', 'start'],
    I + '$Air_Smash': ['<init>', 'tick'],
    I + '$Body_Check_Attack': ['<init>', 'test', 'tick'],
    I + '$Combo1': ['<init>', 'tick'],
    I + '$Combo2': ['<init>', 'start', 'stop', 'tick'],
    I + '$Earth_Shudders': ['<init>', 'tick'],
    I + '$Hornzontal_Small_SwingGoal': ['<init>', 'test', 'tick'],
    I + '$Hornzontal_SwingGoal': ['<init>', 'tick'],
    I + '$Poked': ['<init>', 'tick'],
    I + '$PokeGoal': ['<init>', 'tick'],
    I + '$PredictiveChargeAttackAnimationGoal': ['<init>', 'start', 'stop', 'tick'],
    I + '$Reinforced_Air_Smash': ['<init>', 'test', 'tick'],
    I + '$Shield_Smash': ['<init>', 'tick'],
    I + '$Swing_Attack_Goal': ['<init>', 'tick'],
    MOVE: ['<init>', 'canUse', 'canContinueToUse', 'start', 'stop', 'tick',
           'requiresUpdateEveryTick'],
    HOLD: ['<init>', 'tick'],
    F: ['<init>', 'setUp', 'onHit', 'onHitBlock', 'hurt', 'isPickable',
        'defineSynchedData', 'addAdditionalSaveData', 'readAdditionalSaveData',
        'isSoul', 'setSoul', 'getFired', 'setFired'],
    A: ['<init>', 'setUp', 'onHit', 'onHitBlock', 'hurt', 'isPickable',
        'getPickRadius', 'defineSynchedData', 'addAdditionalSaveData',
        'readAdditionalSaveData', 'getTotalBounces', 'setTotalBounces',
        'getFired', 'setFired'],
    P: ['<init>', 'tick', 'canHitEntity', 'getClipType', 'getInertia',
        'getLiquidInertia', 'shouldBurn', 'addAdditionalSaveData',
        'readAdditionalSaveData', 'onDeflection'],
    S: ['<init>', 'defineSynchedData', 'getRadius', 'setRadius', 'getDamage',
        'setDamage', 'getHpDamage', 'setHpDamage', 'setOwner', 'getOwner',
        'getDuration', 'setDuration', 'getWaitTime', 'setWaitTime', 'setWaiting',
        'isWaiting', 'setSee', 'isSee', 'isSoul', 'setSoul', 'getDimensions',
        'refreshDimensions', 'onSyncedDataUpdated', 'addAdditionalSaveData',
        'readAdditionalSaveData'],
    X: ['<init>', 'makeDamageCalculator', 'getSeenPercent', 'explode',
        'interactsWithBlocks', 'getIndirectSourceEntityInternal',
        'getIndirectSourceEntity', 'getDirectSourceEntity'],
    W: ['get', 'isIgnisDefeatedOnce', 'setIgnisDefeatedOnce'],
    REGISTRY: ['lambda$static$41', 'lambda$static$42', 'lambda$static$45'],
}
FRAGMENTS = {
    I: {'registerGoals': [[0, 220], [245, 264], [289, 441], [467, 767]],
        '<clinit>': [[0, 45], [56, 85], [96, 222], [233, 337]]},
    # Combat timer/retargeting, excluding trail buffer maintenance.
    F: {'tick': [[0, 235]]}, A: {'tick': [[0, 230]]},
    # Waiting/lifecycle/damage dispatch; client particle/sound branch omitted.
    S: {'tick': [[0, 21], [312, 556]]},
    # KEEP bypass and fire placement only; particles/loot loop omitted.
    X: {'finalizeExplosion': [[63, 67], [293, 295], [465, 580]]},
    W: {'load': [[18, 29]], 'save': [[10, 21]]},
    REGISTRY: {'<clinit>': [[709, 740], [777, 791]]},
}
RESOURCES = {
    'team-tag': 'data/cataclysm/tags/entity_type/team_ignis.json',
    'poke-tag': 'data/cataclysm/tags/entity_type/ignis_cant_poke.json',
    'immune-tag': 'data/cataclysm/tags/block/ignis_immune.json',
    'cracked-tag': 'data/cataclysm/tags/block/ignis_can_destroy_cracked_block.json',
}


def specification():
    rows = [dict(id='cataclysm:ignis-offense:' + n, mod_key='cataclysm',
        entry=PKG + n + '.class', methods=methods,
        **({'method_fragments': FRAGMENTS[n]} if n in FRAGMENTS else {}))
        for n, methods in sorted(METHODS.items())]
    rows.extend(dict(id='cataclysm:ignis-offense:' + k, mod_key='cataclysm', entry=v)
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
                if spec['entry'] in [PKG + n + '.class' for n in [I, F, A, P, S]]:
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
                    row['registration_bootstraps'] = [dict(index=i, handle=c.resolve(bs[i][0]),
                        arguments=[c.resolve(a) for a in bs[i][1]]) for i in [68, 71, 72, 155, 156, 159]]
            else:
                row['data'] = json.loads(raw)
            witnesses.append(row)
    return dict(schema='tno.external_effects.native_evidence.v1', baseline=BASELINE,
        status='STATIC_EVIDENCE', witnesses=witnesses,
        note='Missing Ignis offense/owned fireball/flame-strike/explosion methods only. '
             'Locked admission/shared/status/Guardian/Monstrosity and Vanilla witnesses '
             'not regenerated. No runtime, Stage or whole-mod completeness claim.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('jar', type=Path, help='Exact pinned Cataclysm 3.27 JAR')
    evidence = collect(parser.parse_args().jar)
    write_json(SPEC_FILE, specification())
    write_json(EVIDENCE_FILE, evidence)
    print(f'Ignis offense: {len(evidence["witnesses"])} scoped witnesses captured')
