"""Index literals in the existing finite string-keyed NBT-call queue.

The keyword census does not retain all LDC strings. This bounded lookup aid
reads only census methods with a native CompoundTag string-key call, checks
their original hashes, and records all their literal strings. It never infers
which argument a string supplies, reachability, exclusions or semantic closure.
Dynamic keys can be absent from this index; absence is not a coverage proof.
"""
import argparse
from collections import defaultdict
from pathlib import Path
import zipfile

from catalog_common import OUT, byte_hash, read_json, sha256, write_json
from classfile import ClassFile
from collect_combat_census import decode_sites


def selected_methods(census):
    return [m for m in census['methods'] if any(
        i['operand'].startswith('net/minecraft/nbt/CompoundTag.')
        and '(Ljava/lang/String;' in i['operand']
        for i in decode_sites(census, m, 'calls'))]


def index(census, read_entry):
    selected = selected_methods(census)
    grouped = defaultdict(list)
    for m in selected:
        grouped[m['entry']].append(m)
    classes = {c['entry']: c for c in census['classes']}
    rows = []
    for entry, methods in sorted(grouped.items()):
        raw = read_entry(entry)
        assert byte_hash(raw) == classes[entry]['entry_sha256'], ('Changed class', entry)
        cls = ClassFile(raw)
        native = {(m['name'], m['descriptor']): m for m in cls.methods}
        for expected in sorted(methods, key=lambda m: (m['method'], m['descriptor'])):
            m = native[(expected['method'], expected['descriptor'])]
            assert byte_hash(m.get('code', b'')) == expected['code_sha256'], ('Changed method', entry, m['name'])
            literals = [i for i in cls.instructions(m.get('code', b''))
                        if i['opcode'] in ('0x12', '0x13') and isinstance(i['operand'], str)
                        and cls.cp[int.from_bytes(m['code'][i['offset']+1:i['offset']+(2 if i['opcode']=='0x12' else 3)], 'big')][0] == 8]
            rows.append(dict(entry=entry, method=m['name'], descriptor=m['descriptor'],
                             entry_sha256=classes[entry]['entry_sha256'], code_sha256=expected['code_sha256'],
                             literal_strings=[dict(offset=i['offset'], value=i['operand']) for i in literals]))
    return dict(schema='tno.external_effects.native_data_literal_index.v1', mod_key=census['mod_key'],
                jar_sha256=census['jar_sha256'], semantic_coverage_granted=False,
                scope=__doc__.strip(), summary=dict(selected_classes=len(grouped), selected_methods=len(rows)),
                methods=rows)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('mod_key'); p.add_argument('jar', type=Path); p.add_argument('output', type=Path)
    args = p.parse_args(); census = read_json(OUT / (args.mod_key + '-combat-census.json'))
    assert sha256(args.jar) == census['jar_sha256']
    with zipfile.ZipFile(args.jar) as jar:
        result = index(census, jar.read)
    write_json(args.output, result); print(result['summary'])
