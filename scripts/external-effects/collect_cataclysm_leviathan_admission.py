"""Bounded R2k9a Leviathan admission/state/encounter witnesses.

Exact entries from the pinned JAR only. Shared/status/prior boss contracts and
attribute registration are reused; all Leviathan offense/payloads are deferred.
"""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

from catalog_common import BASELINE, OUT, read_json, write_json
from classfile import ClassFile, Reader

PKG = 'com/github/L_Ender/cataclysm/'
L = 'entity/AnimationMonster/BossMonsters/The_Leviathan/The_Leviathan_Entity'
PART = 'entity/AnimationMonster/BossMonsters/The_Leviathan/The_Leviathan_Part'
PART_BASE = 'entity/partentity/Cm_Part_Entity'
ALTAR = 'blockentities/AltarOfAbyss_Block_Entity'
BLOCK = 'blocks/Altar_Of_Abyss_Block'
REGISTRY = 'init/ModEntities'
SPEC_FILE = OUT / 'native-specifications/cataclysm-leviathan-admission.json'
EVIDENCE_FILE = OUT / 'native-evidence/cataclysm-leviathan-admission.json'
METHODS = {
    L: ['hurt', 'isInvulnerableTo', 'DamageCap', 'DpsCap', 'DpsMulti',
        'RangeLimit', 'NatureRegen', 'HealCooldown', 'defineSynchedData',
        'getMeltDown', 'setMeltDown', 'isMeltDown', 'getBlastChance',
        'setBlastChance', 'getModeChance', 'setModeChance',
        'addAdditionalSaveData', 'readAdditionalSaveData',
        'canInFluidType', 'increaseAirSupply', 'isPushedByFluid',
        'onInsideBubbleColumn', 'onAboveBubbleCol', 'leviathan',
        'attackEntityFromPart', 'isMultipartEntity', 'getParts'],
    PART: ['<init>', 'hurt', 'isPickable', 'canBeCollidedWith',
        'addAdditionalSaveData', 'readAdditionalSaveData', 'is', 'getDimensions'],
    # Its header is already locked; only this missing constructor body is new.
    PART_BASE: ['<init>'],
    ALTAR: ['<init>', 'commonTick', 'getItem', 'getItems', 'placeItem',
        'getMaxStackSize', 'markUpdated', 'loadAdditional', 'saveAdditional',
        'BlockBreaking'],
    BLOCK: ['<init>', 'useItemOn', 'newBlockEntity', 'getTicker',
        'getStateForPlacement', 'getFluidState'],
    REGISTRY: ['lambda$static$27'],
}
FRAGMENTS = {
    L: {'<init>': [[0, 3], [101, 132], [169, 174], [212, 305]],
        'tick': [[0, 1], [689, 731]],
        'aiStep': [[0, 1], [2839, 2846], [2899, 2917]],
        '<clinit>': [[52, 57], [135, 141]]},
    # Only admission/clearance/spawn/result/countdown; visual bodies excluded.
    ALTAR: {'tick': [[10, 12], [23, 53], [107, 238], [294, 319]]},
    BLOCK: {'<clinit>': [[11, 20]]},
    REGISTRY: {'<clinit>': [[471, 485]]},
}
RESOURCES = {'altar-clearance-tag': 'data/cataclysm/tags/block/altar_destroy_immune.json'}


def specification():
    rows = [dict(id='cataclysm:leviathan-admission:' + n, mod_key='cataclysm',
        entry=PKG + n + '.class', methods=methods,
        **({'method_fragments': FRAGMENTS[n]} if n in FRAGMENTS else {}))
        for n, methods in sorted(METHODS.items())]
    rows.extend(dict(id='cataclysm:leviathan-admission:' + k,
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
    witnesses = []
    with zipfile.ZipFile(jar_path) as jar:
        for spec in specification()['evidence_specifications']:
            raw = jar.read(spec['entry'])
            row = dict(id=spec['id'], mod_key='cataclysm', jar_sha256=target['sha256'],
                entry=spec['entry'], entry_sha256=hashlib.sha256(raw).hexdigest())
            if spec['entry'].endswith('.class'):
                c = ClassFile(raw)
                row.update(class_name=c.name, superclass=c.super,
                           interfaces=c.interfaces, methods=[])
                if spec['entry'] in [PKG + n + '.class' for n in [L, PART, PART_BASE]]:
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
                if spec['entry'] in [PKG + n + '.class' for n in [REGISTRY, BLOCK]]:
                    r = Reader(next(data for name, data in c.attributes if name == 'BootstrapMethods'))
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
        note='Leviathan concrete incoming hurt/invulnerability/shared bindings, multipart '
             'forwarding, fluid/environment admission, raw phase/counter setters, '
             'combat NBT and exact abyss altar prerequisite/clearance/spawn/NBT only. '
             'Shared hierarchy/status/prior boss/attribute evidence reused. Incoming '
             'rush interruption and phase latch only; all offensive goals/selection, '
             'payloads, terrain-response execution, portal/tongue and defeat callbacks '
             'deferred to R2k9b. Visual method bodies omitted.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('jar', type=Path, help='Exact pinned Cataclysm 3.27 JAR')
    evidence = collect(parser.parse_args().jar)
    write_json(SPEC_FILE, specification())
    write_json(EVIDENCE_FILE, evidence)
    print(f'Leviathan admission: {len(evidence["witnesses"])} scoped witnesses captured')
