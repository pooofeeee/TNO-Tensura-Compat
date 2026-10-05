"""Reproduce an explicit, bounded Cataclysm family specification; no discovery scan."""
import argparse
import hashlib
from pathlib import Path
import zipfile

from catalog_common import BASELINE, OUT, read_json, write_json
from classfile import ClassFile, Reader
from collect_cataclysm_ignited_revenant_offense import instructions


def collect(spec, jar_path):
    target = next(t for t in read_json(OUT / 'jar-inventory.json')['targets'] if t['key'] == 'cataclysm')
    jar_path = Path(jar_path)
    with jar_path.open('rb') as stream:
        assert hashlib.file_digest(stream, 'sha256').hexdigest() == target['sha256']
    assert jar_path.stat().st_size == target['size_bytes']
    witnesses = []
    with zipfile.ZipFile(jar_path) as jar:
        for selected in spec['evidence_specifications']:
            entry = selected['entry']
            assert entry.startswith('com/github/L_Ender/cataclysm/') and entry.endswith('.class')
            raw = jar.read(entry)
            cls = ClassFile(raw)
            row = dict(id=selected['id'], mod_key='cataclysm', jar_sha256=target['sha256'],
                       entry=entry, entry_sha256=hashlib.sha256(raw).hexdigest(),
                       class_name=cls.name, superclass=cls.super, interfaces=cls.interfaces,
                       declared_method_names=sorted({m['name'] for m in cls.methods}), methods=[])
            # A scoped registry absence check reads only this explicitly selected
            # class, rather than discovering or recursively scanning the archive.
            if selected.get('absent_constant_pool_terms'):
                references = [str(cls.resolve(index)) for index in range(1, len(cls.cp))
                              if cls.cp[index] is not None]
                terms = selected['absent_constant_pool_terms']
                assert all(not any(term in value for value in references)
                           for term in terms), (entry, terms)
                row['absent_constant_pool_terms'] = terms
            if selected.get('bootstrap_indices'):
                reader = Reader(next(data for name, data in cls.attributes if name == 'BootstrapMethods'))
                bootstraps = [(reader.u2(), [reader.u2() for _ in range(reader.u2())])
                              for _ in range(reader.u2())]
                row['registration_bootstraps'] = [dict(index=index,
                    handle=cls.resolve(bootstraps[index][0]),
                    arguments=[cls.resolve(arg) for arg in bootstraps[index][1]])
                    for index in selected['bootstrap_indices']]
            for selection in selected['methods']:
                matches = [m for m in cls.methods if m['name'] == selection['name'] and
                           ('descriptor' not in selection or m['descriptor'] == selection['descriptor'])]
                assert matches, (entry, selection)
                for method in matches:
                    code = method.get('code', b'')
                    body = instructions(cls, code)
                    ranges = selection.get('ranges')
                    if ranges:
                        body = [i for i in body if any(a <= i['offset'] <= b for a, b in ranges)]
                        assert all(any(i['offset'] == point for i in body) for span in ranges for point in span)
                    row['methods'].append(dict(name=method['name'], descriptor=method['descriptor'],
                        code_sha256=hashlib.sha256(code).hexdigest(), instructions=body,
                        **({'instruction_offset_ranges': ranges} if ranges else {})))
            witnesses.append(row)
    return dict(schema='tno.external_effects.native_evidence.v1', baseline=BASELINE,
                status='STATIC_EVIDENCE', witnesses=witnesses, note=spec['scope_note'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('spec', type=Path)
    parser.add_argument('jar', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    evidence = collect(read_json(args.spec), args.jar)
    write_json(args.output, evidence)
    print(f'{len(evidence["witnesses"])} exact class witnesses reproduced')
