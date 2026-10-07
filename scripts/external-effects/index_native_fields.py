"""One additive native-field index for an explicitly incomplete keyword census.

Original class/method boundaries and hashes are immutable. This fills the missing
GET/PUT field sites (not another combat discovery/semantic pass). Readonly lookup
consumers must reuse the result; no reachability, exclusion or closure is granted.
ConstantValue inlining, reflection and string-keyed NBT remain separate contexts.
"""
import argparse
import json
import zipfile
from pathlib import Path
from collections import defaultdict
from classfile import ClassFile
from catalog_common import OUT,read_json,write_json,sha256,byte_hash


def index(census,read_entry,selection=None,include_external=False):
    owners={c['name'] for c in census['classes']}
    expected=defaultdict(dict)
    for m in census['methods']:expected[m['entry']][(m['method'],m['descriptor'])]=m
    selected=set(selection) if selection is not None else None
    if selected is not None:
        assert selected <= {(e,n,d) for e,ms in expected.items() for n,d in ms}
    rows=[];classes_checked=0
    for c in census['classes']:
        if selected is not None and not any(k[0]==c['entry'] for k in selected):continue
        raw=read_entry(c['entry']);assert byte_hash(raw)==c['entry_sha256']
        cls=ClassFile(raw);classes_checked+=1
        wanted={cls.resolve(j) for j,x in enumerate(cls.cp) if x and x[0]==9
                and (include_external or cls.resolve(x[1][0]) in owners)}
        if not wanted:continue
        for m in cls.methods:
            if selected is not None and (c['entry'],m['name'],m['descriptor']) not in selected:continue
            e=expected[c['entry']][(m['name'],m['descriptor'])]
            assert byte_hash(m.get('code',b''))==e['code_sha256']
            body=[i for i in cls.instructions(m.get('code',b'')) if i['opcode'] in {'0xb2','0xb3','0xb4','0xb5'} and i['operand'] in wanted]
            if not body:continue
            rows.append(dict(entry=c['entry'],method=m['name'],descriptor=m['descriptor'],entry_sha256=c['entry_sha256'],
                code_sha256=e['code_sha256'],field_sites=body))
    result=dict(schema='tno.external_effects.native_field_use_index.v1',mod_key=census['mod_key'],jar_sha256=census['jar_sha256'],
                semantic_coverage_granted=False,scope=__doc__.strip(),
                summary=dict(original_census_classes_checked=classes_checked,methods_with_native_field_sites=len(rows),native_field_sites=sum(len(m['field_sites']) for m in rows)),
                methods=sorted(rows,key=lambda r:(r['entry'],r['method'],r['descriptor'])))
    if include_external:
        result.update(owner_scope='ALL_FIELD_OWNERS',scope='Complete GET/PUT sites for exact selected native bodies, including external field owners. No semantic judgment or coverage inferred.')
    if selected is not None:
        result['selection']=[dict(entry=e,method=n,descriptor=d,code_sha256=expected[e][n,d]['code_sha256']) for e,n,d in sorted(selected)]
    return result


def pack(document):
    """Intern exact repeated symbols, without dropping any field site."""
    from copy import deepcopy
    d=deepcopy(document)
    d['symbols']=sorted({i['operand'] for m in d['methods'] for i in m['field_sites']})
    by={s:j for j,s in enumerate(d['symbols'])}
    for m in d['methods']:
        m['field_sites']=[[i['offset'],int(i['opcode'],16),by[i['operand']]] for i in m['field_sites']]
    d['instruction_site_encoding']=['offset','opcode','symbol_index']
    return d


def write_index(path,document):
    arrays=('methods','symbols')
    header=json.dumps({k:v for k,v in document.items() if k not in arrays},ensure_ascii=False,indent=2)
    chunks=[header[:-2]]
    for k in arrays:
        chunks+= [',\n  '+json.dumps(k)+': [\n',
                  ',\n'.join('    '+json.dumps(v,ensure_ascii=False,separators=(',',':')) for v in document[k]),'\n  ]']
    Path(path).write_text(''.join(chunks)+'\n}\n',encoding='utf-8')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('mod_key');p.add_argument('jar',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
    c=read_json(OUT/f'{a.mod_key}-combat-census.json');assert sha256(a.jar)==c['jar_sha256']
    with zipfile.ZipFile(a.jar) as z:d=index(c,z.read)
    write_index(a.output,pack(d));print(d['summary'])
