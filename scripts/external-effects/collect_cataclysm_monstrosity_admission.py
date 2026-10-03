"""Capture missing R2k4a admission/setup witnesses from the pinned Cataclysm JAR.

Only explicit entries/methods and two bounded registration fragments are read.
Shared boss/status, Guardian, native hurt and respawner evidence is reused.
No discovery scan, source generation, offensive payload or runtime execution.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import struct
import zipfile

from catalog_common import BASELINE, OUT, read_json, write_json
from classfile import ClassFile, Reader

PKG = 'com/github/L_Ender/cataclysm/'
M = 'entity/InternalAnimationMonster/IABossMonsters/NewNetherite_Monstrosity/Netherite_Monstrosity_Entity'
P = 'entity/InternalAnimationMonster/IABossMonsters/NewNetherite_Monstrosity/Netherite_Monstrosity_Part'
S = 'entity/InternalAnimationMonster/AI/InternalStateGoal'
REGISTRY = 'init/ModEntities'
POOL = 'data/cataclysm/worldgen/template_pool/soul_black_smith/mob/monstrosity.json'
TEMPLATE = 'data/cataclysm/structure/monstrosity.nbt'
SPEC_FILE = OUT / 'native-specifications/cataclysm-monstrosity-admission.json'
EVIDENCE_FILE = OUT / 'native-evidence/cataclysm-monstrosity-admission.json'
METHODS = {
    M: ['<init>', 'netherite_monstrosity', 'hurt', 'hurtParts',
        'attackEntityFromPart', 'DamageCap', 'DpsCap', 'RangeLimit', 'NatureRegen',
        'defineSynchedData', 'isSleep', 'isBerserk', 'setIsBerserk', 'getIsBerserk',
        'setIsAwaken', 'getIsAwaken', 'setMagazine', 'getMagazine',
        'addAdditionalSaveData', 'readAdditionalSaveData', 'finalizeSpawn',
        'die', 'deathtimer', 'AfterDefeatBoss', 'isMultipartEntity', 'getParts', 'canBeCollidedWith'],
    P: ['<init>', 'hurt', 'isPickable', 'canBeCollidedWith', 'is'],
    M + '$NMDoNothingGoal': ['<init>', 'canUse', 'tick', 'stop',
                            'isInterruptable', 'requiresUpdateEveryTick'],
    M + '$3': ['<init>', 'start', 'tick'],
    M + '$MonstrosityPhaseChangeGoal': ['<init>', 'canUse', 'start', 'stop',
                                      'canContinueToUse'],
    S: ['<init>', 'canUse', 'start', 'stop', 'canContinueToUse',
        'isInterruptable', 'requiresUpdateEveryTick'],
    REGISTRY: ['lambda$static$2'],
    # Declaration inventory only; prove the concrete part's Cataclysm parent
    # does not add an isInvulnerableTo override. No sync/render utility capture.
    'entity/partentity/Cm_Part_Entity': [],
}
FRAGMENTS = {
    M: dict(registerGoals=[180, 237], tick=[0, 1]),  # setup registrations; inherited tick call only
    REGISTRY: dict(**{'<clinit>': [46, 60]}),  # instruction start offsets, exact registration only
}
DESCRIPTORS = {S: {'<init>': '(L' + PKG +
    'entity/InternalAnimationMonster/Internal_Animation_Monster;IIIII)V'}}
COMBAT_NBT_KEYS = ['id', 'Health', 'is_Awaken', 'is_Berserk', 'Magazine',
    'Invulnerable', 'PersistenceRequired', 'NoAI', 'Attributes', 'AttackState',
    'LifeRemain', 'Home', 'HomePos', 'HomePoint', 'HomeDimension']


def specification():
    rows = [dict(id='cataclysm:monstrosity-admission:' + name, mod_key='cataclysm',
                 entry=PKG + name + '.class', methods=names,
                 **({'method_fragments': FRAGMENTS[name]} if name in FRAGMENTS else {}),
                 **({'method_descriptors': DESCRIPTORS[name]} if name in DESCRIPTORS else {}))
            for name, names in sorted(METHODS.items())]
    rows.extend([
        dict(id='cataclysm:monstrosity-admission:encounter-pool', mod_key='cataclysm', entry=POOL),
        dict(id='cataclysm:monstrosity-admission:encounter-template', mod_key='cataclysm',
             entry=TEMPLATE, entity_id='cataclysm:netherite_monstrosity',
             selected_nbt_keys=COMBAT_NBT_KEYS),
    ])
    return dict(schema='tno.external_effects.native_specification.v1', baseline=BASELINE,
                evidence_specifications=rows)


def template_entities(raw):
    """Decode this one small native template, retain only entity combat setup."""
    data = gzip.decompress(raw)
    offset = 0

    def take(n):
        nonlocal offset
        assert n >= 0 and offset + n <= len(data)
        value = data[offset:offset + n]
        offset += n
        return value

    def number(fmt):
        return struct.unpack('>' + fmt, take(struct.calcsize('>' + fmt)))[0]

    def string():
        return take(number('H')).decode('utf-8')

    def payload(tag):
        if tag in [1, 2, 3, 4, 5, 6]:
            return number({1: 'b', 2: 'h', 3: 'i', 4: 'q', 5: 'f', 6: 'd'}[tag])
        if tag == 7:
            return list(take(number('i')))
        if tag == 8:
            return string()
        if tag == 9:
            kind, count = number('B'), number('i')
            assert count >= 0
            return [payload(kind) for _ in range(count)]
        if tag == 10:
            result = {}
            while True:
                kind = number('B')
                if kind == 0:
                    return result
                key = string()
                assert key not in result
                result[key] = payload(kind)
        if tag in [11, 12]:
            count = number('i')
            assert count >= 0
            return [number('i' if tag == 11 else 'q') for _ in range(count)]
        raise ValueError(tag)

    assert number('B') == 10
    root_name = string()
    root = payload(10)
    assert offset == len(data)
    entities = [{k: entity['nbt'][k] for k in COMBAT_NBT_KEYS if k in entity['nbt']}
                for entity in root['entities']
                if entity['nbt'].get('id') == 'cataclysm:netherite_monstrosity']
    return dict(decompressed_sha256=hashlib.sha256(data).hexdigest(),
                root_name=root_name, entities=entities,
                scope='Only native Monstrosity entity combat setup. Legacy attribute keys '
                      'are literal NBT, not a claim about loader conversion/effective values.')


def collect(jar_path):
    target = next(t for t in read_json(OUT / 'jar-inventory.json')['targets'] if t['key'] == 'cataclysm')
    jar_path = Path(jar_path)
    with jar_path.open('rb') as stream:
        assert hashlib.file_digest(stream, 'sha256').hexdigest() == target['sha256']
    assert jar_path.stat().st_size == target['size_bytes']
    witnesses = []
    with zipfile.ZipFile(jar_path) as jar:
        for spec in specification()['evidence_specifications']:
            data = jar.read(spec['entry'])
            row = dict(id=spec['id'], mod_key='cataclysm', jar_sha256=target['sha256'],
                       entry=spec['entry'], entry_sha256=hashlib.sha256(data).hexdigest())
            if spec['entry'].endswith('.class'):
                c = ClassFile(data)
                row.update(class_name=c.name, superclass=c.super, interfaces=c.interfaces, methods=[])
                if spec['entry'] in [PKG + M + '.class', PKG + 'entity/partentity/Cm_Part_Entity.class']:
                    row['declared_method_names'] = sorted({m['name'] for m in c.methods})
                for name in spec['methods'] + list(spec.get('method_fragments', {})):
                    descriptor = spec.get('method_descriptors', {}).get(name)
                    selected = [m for m in c.methods if m['name'] == name
                                and (descriptor is None or m['descriptor'] == descriptor)]
                    assert selected, (spec['entry'], name)
                    for m in selected:
                        code = m.get('code', b'')
                        ins = list(c.instructions(code))
                        fragment = spec.get('method_fragments', {}).get(name)
                        if fragment:
                            ins = [i for i in ins if fragment[0] <= i['offset'] <= fragment[1]]
                            assert ins and ins[0]['offset'] == fragment[0] and ins[-1]['offset'] == fragment[1]
                        row['methods'].append(dict(name=name, descriptor=m['descriptor'],
                            code_sha256=hashlib.sha256(code).hexdigest(), instructions=ins,
                            **({'instruction_offset_range': fragment} if fragment else {})))
                if spec['entry'] == PKG + REGISTRY + '.class':
                    r = Reader(next(raw for name, raw in c.attributes if name == 'BootstrapMethods'))
                    bootstraps = [(r.u2(), [r.u2() for _ in range(r.u2())]) for _ in range(r.u2())]
                    row['registration_bootstraps'] = [
                        dict(index=i, handle=c.resolve(bootstraps[i][0]),
                             arguments=[c.resolve(a) for a in bootstraps[i][1]]) for i in [111, 116]]
            elif spec['entry'] == TEMPLATE:
                row['data'] = template_entities(data)
            else:
                row['data'] = json.loads(data)
            witnesses.append(row)
    return dict(schema='tno.external_effects.native_evidence.v1', baseline=BASELINE,
                status='STATIC_EVIDENCE', witnesses=witnesses,
                note='Pinned Monstrosity admission/setup only; inherited/status/Guardian/native '
                     'contracts are reused. No offensive payload review or runtime validation.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('jar', type=Path, help='Exact pinned Cataclysm 3.27 JAR')
    evidence = collect(parser.parse_args().jar)
    write_json(SPEC_FILE, specification())
    write_json(EVIDENCE_FILE, evidence)
    print(f'Monstrosity admission: {len(evidence["witnesses"])} scoped witnesses captured')
