"""Capture only new R2k11b Ender Golem offense witnesses from the pinned JAR.

Reuse the previously closed Void Rune, shared lifecycle/repulsion and alliance
tag witnesses. Root fragments exclude all protected R2k11a instruction offsets.
"""
import argparse
import hashlib
from pathlib import Path
import zipfile

from catalog_common import BASELINE, OUT, read_json, write_json
from classfile import ClassFile
from collect_cataclysm_ender_golem_admission import instructions as branch_instructions

PKG = 'com/github/L_Ender/cataclysm/'
G = 'entity/AnimationMonster/BossMonsters/Ender_Golem_Entity'
PURSUIT = 'entity/AI/CmAttackGoal'
TERRAIN = 'data/cataclysm/tags/block/ender_golem_can_destroy.json'
SPEC_FILE = OUT / 'native-specifications/cataclysm-ender-golem-offense.json'
EVIDENCE_FILE = OUT / 'native-evidence/cataclysm-ender-golem-offense.json'
METHODS = {
    G: ['getAnimations', 'getRandomAttack', 'BlockBreaking', 'EarthQuake',
        'VoidRuneAttack', 'spawnFangs', 'launch', 'isAlliedTo', 'repelEntities',
        'getDeathAnimation'],
    G + '$AttackGoal': ['<init>', 'canUse', 'requiresUpdateEveryTick', 'stop', 'tick'],
    G + '$AwakenGoal': ['<init>', 'canUse', 'requiresUpdateEveryTick', 'tick'],
    PURSUIT: ['<init>', 'canUse', 'stop', 'tick'],
}
FRAGMENTS = {
    G: {'<clinit>': [[0, 37]], 'tick': [[4, 17], [125, 581]],
        'registerGoals': [[0, 46]], 'onDeathAIUpdate': [[0, 14]]},
}


def instructions(c, code):
    result = branch_instructions(c, code)
    for i in result:
        if 0x15 <= int(i['opcode'], 16) <= 0x19 or 0x36 <= int(i['opcode'], 16) <= 0x3a:
            i['local_index'] = code[i['offset'] + 1]
    return result


def specification():
    entries = [dict(id='cataclysm:ender-golem-offense:' + n, mod_key='cataclysm',
        entry=PKG + n + '.class', methods=methods,
        method_fragments=FRAGMENTS.get(n, {})) for n, methods in sorted(METHODS.items())]
    entries.append(dict(id='cataclysm:ender-golem-offense:data:' + TERRAIN,
        mod_key='cataclysm', entry=TERRAIN, kind='RESOURCE'))
    return dict(schema='tno.external_effects.native_specification.v1',
        baseline=BASELINE, evidence_specifications=entries)


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
            if spec.get('kind') == 'RESOURCE':
                row['raw_text'] = raw.decode('utf-8')
            else:
                c = ClassFile(raw)
                row.update(class_name=c.name, superclass=c.super,
                    interfaces=c.interfaces, methods=[])
                for name in spec['methods'] + list(spec['method_fragments']):
                    matches = [m for m in c.methods if m['name'] == name]
                    assert matches, (spec['entry'], name)
                    for m in matches:
                        code = m.get('code', b'')
                        ins = instructions(c, code)
                        ranges = spec['method_fragments'].get(name)
                        if ranges:
                            ins = [i for i in ins if any(a <= i['offset'] <= b for a, b in ranges)]
                            assert all(any(i['offset'] == v for i in ins) for span in ranges for v in span)
                        row['methods'].append(dict(name=name, descriptor=m['descriptor'],
                            code_sha256=hashlib.sha256(code).hexdigest(), instructions=ins,
                            **({'instruction_offset_ranges': ranges} if ranges else {})))
            witnesses.append(row)
    return dict(schema='tno.external_effects.native_evidence.v1', baseline=BASELINE,
        status='STATIC_EVIDENCE', witnesses=witnesses,
        note='Four exact offense/registered-goal classes and one terrain allowlist. '
             'Protected incoming/awake/heal/NBT/encounter fragments excluded. '
             'Existing Void Rune payload, team tag, repulsion/query and death contracts '
             'reused without regeneration. No recursive scan, runtime or Stage decisions.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('jar', type=Path, help='Exact pinned Cataclysm 3.27 JAR')
    evidence = collect(parser.parse_args().jar)
    write_json(SPEC_FILE, specification())
    write_json(EVIDENCE_FILE, evidence)
    print(f'Ender Golem offense: {len(evidence["witnesses"])} scoped witnesses captured')
