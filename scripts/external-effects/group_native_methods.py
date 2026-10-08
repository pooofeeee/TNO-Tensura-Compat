"""Group exact resolved native bodies for review, granting no semantic coverage.

Reuse captured instructions and the existing SELF-only/bootstrap comparator.
Method names, descriptors, access, superclass, local slots, branches, exception
tables and typed bootstrap signatures all remain part of the equality key.
"""
import argparse
from collections import defaultdict
import json
from pathlib import Path
import zipfile

from catalog_common import read_json, write_json, sha256, byte_hash
from classfile import ClassFile
from compare_native_methods import normalized, referenced_bootstraps, bootstrap_signature


def signature(witness, method, access, bootstraps):
    return dict(superclass=witness['superclass'], name=method['name'],
        descriptor=method['descriptor'], access=access,
        instructions=normalized(method['instructions'], witness['class_name']),
        exception_handlers=method.get('exception_handlers', []),
        bootstraps=bootstraps)


def group(census, evidence, jar):
    assert sha256(jar) == census['jar_sha256']
    native={(m['entry'],m['method'],m['descriptor']):m for m in census['methods']}
    classes={c['entry']:c for c in census['classes']}
    groups=defaultdict(list)
    with zipfile.ZipFile(jar) as archive:
        for w in evidence['witnesses']:
            if not w['entry'].endswith('.class'):continue
            assert w['jar_sha256']==census['jar_sha256']
            assert w['entry_sha256']==classes[w['entry']]['entry_sha256']
            cls=None
            for m in w['methods']:
                assert not m.get('instruction_offset_ranges'), 'Partial evidence cannot prove equality'
                key=(w['entry'],m['name'],m['descriptor']);n=native[key]
                assert n['code_sha256']==m['code_sha256']
                indices=referenced_bootstraps(m['instructions'])
                if indices and cls is None:
                    raw=archive.read(w['entry']);assert byte_hash(raw)==w['entry_sha256']
                    cls=ClassFile(raw)
                boot={str(i):bootstrap_signature(cls,i) for i in indices}
                sig=signature(w,m,n['access'],boot)
                encoded=json.dumps(sig,sort_keys=True,separators=(',',':'))
                groups[encoded].append(dict(entry=key[0],method=key[1],descriptor=key[2],
                    code_sha256=n['code_sha256']))
    rows=[dict(signature_sha256=byte_hash(sig.encode()),
               template=sorted(ms,key=lambda m:(m['entry'],m['method'],m['descriptor']))[0],
               members=sorted(ms,key=lambda m:(m['entry'],m['method'],m['descriptor'])))
          for sig,ms in groups.items()]
    rows.sort(key=lambda r:(r['template']['entry'],r['template']['method'],r['template']['descriptor']))
    return dict(schema='tno.external_effects.exact_body_review_groups.v1',
        mod_key=census['mod_key'],jar_sha256=census['jar_sha256'],
        scope=__doc__.strip(),semantic_coverage_granted=False,groups=rows,
        summary=dict(captured_methods=sum(len(r['members']) for r in rows),
            distinct_review_bodies=len(rows),repeated_groups=sum(len(r['members'])>1 for r in rows),
            repeated_members=sum(len(r['members']) for r in rows if len(r['members'])>1),
            redundant_body_reviews=sum(len(r['members'])-1 for r in rows)))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('census',type=Path);p.add_argument('evidence',type=Path)
    p.add_argument('--jar',required=True,type=Path);p.add_argument('--output',required=True,type=Path)
    a=p.parse_args();d=group(read_json(a.census),read_json(a.evidence),a.jar)
    d['input_hashes']=dict(census=sha256(a.census),evidence=sha256(a.evidence))
    write_json(a.output,d);print(d['summary'])
