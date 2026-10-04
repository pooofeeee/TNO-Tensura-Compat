"""Capture only new R2k13b Berserker offense/goal witnesses.

Reuse the captured AreaAttack/AreaSwordAttack, shared goals, raw state, source,
Blazing Brand, shield, nearby-query, repulsion and admission contracts.
"""
import argparse
import hashlib
from pathlib import Path
import zipfile

from catalog_common import BASELINE, OUT, read_json, write_json
from classfile import ClassFile
from collect_cataclysm_ignited_revenant_offense import instructions

PKG = 'com/github/L_Ender/cataclysm/'
B = 'entity/InternalAnimationMonster/Ignited_Berserker_Entity'
S = 'entity/InternalAnimationMonster/AI/InternalStateGoal'
SPEC_FILE = OUT / 'native-specifications/cataclysm-ignited-berserker-offense.json'
EVIDENCE_FILE = OUT / 'native-evidence/cataclysm-ignited-berserker-offense.json'
METHODS = {
    B: ['isAlliedTo'],
    B+'$1': ['<init>', 'canUse'],
    B+'$2': ['<init>', 'canUse', 'stop'],
    B+'$3': ['<init>', 'canUse', 'stop'],
    B+'$4': ['<init>', 'canUse'],
    B+'$5': ['<init>', 'stop'],
    S: ['<init>', 'tick'],
}
DESCRIPTORS = {S: {'<init>': ['(L'+PKG+'entity/InternalAnimationMonster/Internal_Animation_Monster;IIIIIZ)V']}}
FRAGMENTS = {B: {
    'tick': [[0,36], [82,136]],
    'registerGoals': [[57,265]],
    'aiStep': [[0,57], [77,105], [125,408], [428,451], [471,496], [516,539],
               [559,646], [666,689], [709,734], [754,779], [799,818]],
}}


def specification():
    return dict(schema='tno.external_effects.native_specification.v1', baseline=BASELINE,
        evidence_specifications=[dict(id='cataclysm:ignited-berserker-offense:'+n,
            mod_key='cataclysm', entry=PKG+n+'.class', methods=methods,
            method_fragments=FRAGMENTS.get(n, {}), method_descriptors=DESCRIPTORS.get(n, {}))
            for n, methods in sorted(METHODS.items())])


def collect(jar_path):
    target = next(t for t in read_json(OUT/'jar-inventory.json')['targets'] if t['key']=='cataclysm')
    jar_path = Path(jar_path)
    with jar_path.open('rb') as stream:
        assert hashlib.file_digest(stream, 'sha256').hexdigest()==target['sha256']
    assert jar_path.stat().st_size==target['size_bytes']
    witnesses, sword_callers = [], []
    with zipfile.ZipFile(jar_path) as jar:
        for spec in specification()['evidence_specifications']:
            raw = jar.read(spec['entry'])
            c = ClassFile(raw)
            row = dict(id=spec['id'], mod_key='cataclysm', jar_sha256=target['sha256'],
                entry=spec['entry'], entry_sha256=hashlib.sha256(raw).hexdigest(),
                class_name=c.name, superclass=c.super, interfaces=c.interfaces, methods=[])
            for name in spec['methods']+list(spec['method_fragments']):
                matches = [m for m in c.methods if m['name']==name and (
                    name not in spec['method_descriptors'] or m['descriptor'] in spec['method_descriptors'][name])]
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
                        **({'instruction_offset_ranges':ranges} if ranges else {})))
            if spec['entry'].startswith(PKG+B):
                # A bounded exact-name caller check; do not recapture old method bodies.
                for m in c.methods:
                    for i in instructions(c,m.get('code',b'')):
                        if i['opcode'] in {'0xb6','0xb7','0xb8','0xb9','0xba'} and (
                            PKG+B+'.AreaSwordAttack(' in str(i['operand'])):
                            sword_callers.append(dict(entry=spec['entry'],method=m['name'],
                                descriptor=m['descriptor'],offset=i['offset']))
            witnesses.append(row)
    return dict(schema='tno.external_effects.native_evidence.v1', baseline=BASELINE,
        status='STATIC_EVIDENCE', witnesses=witnesses,
        area_sword_caller_check=dict(scope=[PKG+B+'.class']+[PKG+B+'$'+str(i)+'.class' for i in range(1,6)],
            exact_target=PKG+B+'.AreaSwordAttack(FFFFF)V', callers=sword_callers),
        note='Seven exact entries: Berserker offense fragments/alliance, its five directly '
             'registered goals, and only the newly reached boolean InternalStateGoal constructor/tick. '
             'Sounds, visual state methods and utility goals excluded. Existing area helpers and '
             'protected admission/shared/native/status/repulsion/owner-source witnesses reused '
             'without recapture. No owned attack entity reached, recursive JAR scan, runtime or Stage policy.')


if __name__=='__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('jar', type=Path, help='Exact pinned Cataclysm 3.27 JAR')
    evidence = collect(parser.parse_args().jar)
    write_json(SPEC_FILE, specification())
    write_json(EVIDENCE_FILE, evidence)
    print(f'Ignited Berserker offense: {len(evidence["witnesses"])} scoped witnesses captured')
