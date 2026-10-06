"""Reproduce only new evidence and exact Cataclysm methods affected by repair."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile

from catalog_common import OUT, ROOT, read_json
from classfile import ClassFile
from collect_cataclysm_family import collect as collect_methods
from collect_catalog_reachability import collect as collect_callers
from collect_cataclysm_ignited_revenant_offense import instructions


def reproduce(jar):
    note=read_json(OUT/'cataclysm-r2k34-integrity-closure.json')
    assert collect_methods(read_json(OUT/note['specification_file']),jar)==read_json(OUT/note['evidence_file'])
    assert collect_callers(jar)==read_json(OUT/note['reachability_file'])
    report=read_json(OUT/'catalog-integrity-repairs.json')
    path=(OUT/'mod-reviews/cataclysm.json').relative_to(ROOT).as_posix()
    previous=json.loads(subprocess.check_output(['git','show',report['starting_sha']+':'+path],cwd=ROOT))
    old_ids={r['id'] for r in previous['effects']}
    review=read_json(OUT/'mod-reviews/cataclysm.json')
    changed={r['original_id'] for r in report['canonical_record_changes']['cataclysm']}
    rows=[r for r in review['effects'] if r['id'] not in old_ids or r['id'] in changed]
    proofs=[p for r in rows for p in r['implementation'] if p['evidence_file'].startswith('native-evidence/cataclysm')]
    proofs += [p for r in review['native_context_records'] if r.get('original_id') in changed
               for p in r.get('native_context',{}).get('implementation',[])]
    cache={};native={};checked=set();classes=set()
    with zipfile.ZipFile(jar) as archive:
        for proof in proofs:
            if proof['evidence_file'] not in cache:
                cache[proof['evidence_file']]=read_json(OUT/proof['evidence_file'])
            witness=next(w for w in cache[proof['evidence_file']]['witnesses'] if w['entry']==proof['entry'])
            entry=witness['entry']
            if not entry.endswith('.class'):
                assert not proof['methods']
                raw=archive.read(entry)
                assert hashlib.sha256(raw).hexdigest()==witness['entry_sha256']
                continue
            if entry not in native:
                raw=archive.read(entry);native[entry]=ClassFile(raw)
                assert hashlib.sha256(raw).hexdigest()==witness['entry_sha256']
            classes.add(entry)
            cls=native[entry]
            # Empty-method proofs intentionally establish declared-method
            # absence/hierarchy, not an invented executable callback.
            if 'declared_method_names' in witness:
                assert set(witness['declared_method_names'])=={m['name'] for m in cls.methods},entry
            for stored in witness['methods']:
                if stored['name'] not in proof['methods']:
                    continue
                key=entry,stored['name'],stored['descriptor'],proof['evidence_file']
                if key in checked:
                    continue
                method=next(m for m in cls.methods if (m['name'],m['descriptor'])==key[1:3])
                code=method.get('code',b'')
                assert hashlib.sha256(code).hexdigest()==stored['code_sha256'],key
                decoded={i['offset']:i for i in instructions(cls,code)}
                for expected in stored['instructions']:
                    actual=decoded[expected['offset']]
                    assert all(actual.get(k)==v for k,v in expected.items()),(key,expected,actual)
                checked.add(key)
    return dict(status='PASS',new_scoped_evidence='BYTE_IDENTICAL',targeted_callers='BYTE_IDENTICAL',
        affected_class_entries=len(classes),affected_method_witnesses=len(checked),
        whole_jar_semantic_scan=False,runtime_tests=0)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('jar',type=Path)
    print(json.dumps(reproduce(parser.parse_args().jar),sort_keys=True))
