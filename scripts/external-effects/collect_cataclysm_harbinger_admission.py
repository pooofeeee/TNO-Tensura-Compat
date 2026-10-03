"""Capture missing R2k6a Harbinger admission/state/setup witnesses only.

Explicit pinned entries and bounded fragments; no offense or recursive scan.
Locked shared/status and completed family evidence is reused unchanged.
"""
import argparse
import gzip
import struct
import hashlib
import json
from pathlib import Path
import zipfile

from catalog_common import BASELINE, OUT, read_json, write_json
from classfile import ClassFile, Reader

PKG = 'com/github/L_Ender/cataclysm/'
H = 'entity/AnimationMonster/BossMonsters/The_Harbinger_Entity'
BASE = 'entity/AnimationMonster/BossMonsters/LLibrary_Boss_Monster'
MM = 'entity/AnimationMonster/LLibrary_Monster'
AM = 'entity/etc/Animation_Monsters'
AWAKEN = H + '$AwakenGoal'
REGISTRY = 'init/ModEntities'
POOL = 'data/cataclysm/worldgen/template_pool/ancient_factory/mob/the_harbinger.json'
TEMPLATE = 'data/cataclysm/structure/the_harbinger.nbt'
SPEC_FILE = OUT / 'native-specifications/cataclysm-harbinger-admission.json'
EVIDENCE_FILE = OUT / 'native-evidence/cataclysm-harbinger-admission.json'
METHODS = {
    H: ['<init>', 'hurt', 'harbinger', 'DamageCap', 'DpsCap', 'RangeLimit',
        'NatureRegen', 'defineSynchedData', 'addAdditionalSaveData',
        'readAdditionalSaveData', 'mobInteract', 'canBeSeenAsEnemy', 'isPowered',
        'setIsAct', 'getIsAct', 'setIsLaserMode', 'getIsLaserMode',
        'setIsCharge', 'getIsCharge', 'setOverload', 'getOverload',
        'getAlternativeTarget', 'setAlternativeTarget', 'canChangeDimensions'],
    AWAKEN: ['<init>', 'canUse', 'requiresUpdateEveryTick', 'tick'],
    # Declaration-only inheritance/absence checks. Locked bodies stay cold.
    BASE: [], AM: [], MM: [],
    REGISTRY: ['lambda$static$24'],
}
FRAGMENTS = {
    H: {
        'registerGoals': [[0, 13]],
        'aiStep': [[29, 147]],
        'customServerAiStep': [[0, 55], [374, 452], [483, 526]],
        '<clinit>': [[49, 54]],
    },
    REGISTRY: {'<clinit>': [[423, 434]]},
}
COMBAT_NBT_KEYS = ['id', 'Health', 'Is_Act', 'Invulnerable',
    'PersistenceRequired', 'NoAI', 'Attributes', 'Home', 'HomePos',
    'HomePoint', 'HomeDimension']


def specification():
    rows = [dict(id='cataclysm:harbinger-admission:' + n, mod_key='cataclysm',
        entry=PKG + n + '.class', methods=names,
        **({'method_fragments': FRAGMENTS[n]} if n in FRAGMENTS else {}))
        for n, names in sorted(METHODS.items())]
    rows.extend([
        dict(id='cataclysm:harbinger-admission:encounter-pool', mod_key='cataclysm', entry=POOL),
        dict(id='cataclysm:harbinger-admission:encounter-template', mod_key='cataclysm',
             entry=TEMPLATE, entity_id='cataclysm:the_harbinger', selected_nbt_keys=COMBAT_NBT_KEYS),
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
                if entity['nbt'].get('id') == 'cataclysm:the_harbinger']
    return dict(decompressed_sha256=hashlib.sha256(data).hexdigest(),
                root_name=root_name, entities=entities,
                scope='Only native Harbinger entity combat setup. Legacy attribute keys '
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
            raw = jar.read(spec['entry'])
            if spec['entry'] in [POOL, TEMPLATE]:
                witnesses.append(dict(id=spec['id'], mod_key='cataclysm',
                    jar_sha256=target['sha256'], entry=spec['entry'],
                    entry_sha256=hashlib.sha256(raw).hexdigest(),
                    **({'json': json.loads(raw)} if spec['entry'] == POOL else template_entities(raw))))
                continue
            c = ClassFile(raw)
            row = dict(id=spec['id'], mod_key='cataclysm', jar_sha256=target['sha256'],
                entry=spec['entry'], entry_sha256=hashlib.sha256(raw).hexdigest(),
                class_name=c.name, superclass=c.super, interfaces=c.interfaces, methods=[])
            if spec['entry'] in [PKG + n + '.class' for n in [H, BASE, MM, AM]]:
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
                        assert all(any(i['offset'] == v for i in ins) for r in ranges for v in r), (spec['entry'], name, ranges)
                    row['methods'].append(dict(name=name, descriptor=m['descriptor'],
                        code_sha256=hashlib.sha256(code).hexdigest(), instructions=ins,
                        **({'instruction_offset_ranges': ranges} if ranges else {})))
            if spec['entry'] == PKG + REGISTRY + '.class':
                r = Reader(next(data for name, data in c.attributes if name == 'BootstrapMethods'))
                bs = [(r.u2(), [r.u2() for _ in range(r.u2())]) for _ in range(r.u2())]
                indices = [89, 138]
                row['registration_bootstraps'] = [dict(index=i, handle=c.resolve(bs[i][0]),
                    arguments=[c.resolve(a) for a in bs[i][1]]) for i in indices]
            witnesses.append(row)
    return dict(schema='tno.external_effects.native_evidence.v1', baseline=BASELINE,
        status='STATIC_EVIDENCE', witnesses=witnesses,
        note='Harbinger incoming/power/activation/mode/persistence/encounter prerequisites only. '
             'Exact missing methods/fragments and one native entity template/pool; '
             'shared/status/Guardian/Monstrosity/Ignis contracts not regenerated. '
             'Attack selection, offensive goals, terrain payloads and all owned payloads deferred.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('jar', type=Path, help='Exact pinned Cataclysm 3.27 JAR')
    evidence = collect(parser.parse_args().jar)
    write_json(SPEC_FILE, specification())
    write_json(EVIDENCE_FILE, evidence)
    print(f'Harbinger admission: {len(evidence["witnesses"])} scoped witnesses captured')
