"""Prove selected native methods equivalent; normalize only each class's own owner."""
import argparse
import re
import zipfile

from catalog_common import OUT, byte_hash, read_json, sha256, write_json
from classfile import ClassFile
from collect_cataclysm_ignited_revenant_offense import instructions


def normalized(body, owner):
    pattern = re.compile(re.escape(owner) + r'(?=[.;]|$)')
    return [dict(i, operand=pattern.sub('SELF', i['operand'])
                 if isinstance(i.get('operand'), str) else i.get('operand')) for i in body]


def collect(spec, jar_path):
    assert sha256(jar_path) == spec['jar_sha256']
    proof = spec['template']
    witness = next(w for w in read_json(OUT/proof['evidence_file'])['witnesses']
                   if w['id'] == proof['witness_id'])
    template = {(m['name'], m['descriptor']): m for m in witness['methods']
                if m['name'] in spec['methods']}
    rows = []
    with zipfile.ZipFile(jar_path) as jar:
        assert byte_hash(jar.read(witness['entry'])) == witness['entry_sha256']
        for entry in sorted(spec['entries']):
            raw = jar.read(entry)
            cls = ClassFile(raw)
            assert cls.super == witness['superclass']
            selected = [m for m in cls.methods if m['name'] in spec['methods']]
            assert {(m['name'], m['descriptor']) for m in selected} == set(template)
            for method in selected:
                key = method['name'], method['descriptor']
                code = method.get('code', b'')
                body = normalized(instructions(cls, code), cls.name)
                expected = normalized(template[key]['instructions'], witness['class_name'])
                assert body == expected, ('non-equivalent method', entry, key)
                rows.append(dict(entry=entry, entry_sha256=byte_hash(raw), method=key[0],
                                 descriptor=key[1], code_sha256=byte_hash(code),
                                 template_code_sha256=template[key]['code_sha256'],
                                 status='EXACT_RESOLVED_INSTRUCTIONS_EXCEPT_SELF_OWNER'))
    return dict(schema='tno.external_effects.native_method_equivalence.v1',
                mod_key=spec['mod_key'], jar_sha256=spec['jar_sha256'], template=proof,
                normalization='Only exact SELF owner references; other owners, literals, branches and local indexes unchanged.',
                rows=sorted(rows,key=lambda r:(r['entry'],r['method'],r['descriptor'])),
                note='Equality covers only selected method bodies. Pickup contents, other overrides, anonymous subclasses and actual delivery producers remain distinct.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('specification', type=__import__('pathlib').Path)
    parser.add_argument('--jar', required=True, type=__import__('pathlib').Path)
    parser.add_argument('--output', required=True, type=__import__('pathlib').Path)
    args = parser.parse_args()
    result = collect(read_json(args.specification), args.jar)
    write_json(args.output,result)
    print(len(result['rows']), 'exact selected method equivalences')
