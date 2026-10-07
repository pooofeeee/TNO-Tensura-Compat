"""Capture an explicit finite-census scope; capture never establishes coverage."""
import argparse
from pathlib import Path
import subprocess
import zipfile

from catalog_common import OUT, read_json, write_json, sha256
from native_evidence import collect


def prepare(key, label, entries, jar, work=None, decompiler=None, java='java'):
    census = read_json(OUT / f'{key}-combat-census.json')
    assert sha256(jar) == census['jar_sha256']
    entries = sorted(set(entries))
    known = {c['entry'] for c in census['classes']}
    assert entries and set(entries) <= known, 'Scope must come from existing census'
    specifications = []
    for entry in entries:
        methods = [dict(name=m['method'], descriptor=m['descriptor'],
                        include_local_operands=True, include_exception_handlers=True)
                   for m in census['methods'] if m['entry'] == entry]
        specifications.append(dict(id=f'{key}:{label}:{entry}', mod_key=key,
            entry=entry, include_declared_methods=True, include_annotations=True, methods=methods))
    document = dict(schema='tno.external_effects.native_specification.v1',
        mod_key=key, scope='Explicit existing finite-census entries; no discovery, '
        'reachability, semantics, exclusion or completion inferred by capture.',
        evidence_specifications=specifications)
    write_json(OUT / 'native-specifications' / f'{key}-{label}.json', document)
    result = collect(document, {key:jar})
    write_json(OUT / 'native-evidence' / f'{key}-{label}.json', result)
    if decompiler:
        assert work is not None
        work.mkdir(parents=True, exist_ok=True)
        selected = work / 'selected.jar'
        with zipfile.ZipFile(jar) as source, zipfile.ZipFile(selected, 'w') as dest:
            for entry in entries:
                dest.writestr(entry, source.read(entry))
        with (work/'decompile.log').open('w') as log:
            subprocess.run([java, '-jar', str(decompiler), '-log=WARN',
                            '-dgs=1', str(selected), str(work/'sources')],
                           stdout=log, stderr=subprocess.STDOUT, check=True)
    return dict(classes=len(entries), methods=sum(len(w['methods']) for w in result['witnesses']),
                jar_sha256=census['jar_sha256'])


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('mod_key'); p.add_argument('label')
    p.add_argument('--entries', type=Path, required=True)
    p.add_argument('--jar', type=Path, required=True)
    p.add_argument('--work', type=Path); p.add_argument('--decompiler', type=Path)
    p.add_argument('--java', default='java')
    a = p.parse_args()
    entries = [s.strip() for s in a.entries.read_text().splitlines() if s.strip()]
    print(prepare(a.mod_key, a.label, entries, a.jar, a.work, a.decompiler, a.java))
