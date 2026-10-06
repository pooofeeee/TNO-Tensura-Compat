"""Pin manually reviewed claims to installed class/method bytes and archive resources."""
from classfile import ClassFile
from catalog_common import *

def collect(document, jar_paths=None):
    inventory=read_json(OUT/'jar-inventory.json')
    targets={x['key']:x for x in inventory['targets']+inventory['compat_candidates']}
    witnesses=[]; verified={}
    for specification in document['evidence_specifications']:
        target=targets[specification['mod_key']]
        path=(jar_paths or {}).get(target['key'],target['path'])
        if target['key'] not in verified:
            assert sha256(path)==target['sha256']
            verified[target['key']]=path
        with zipfile.ZipFile(path) as jar:
            entry=specification['entry']; data=jar.read(entry)
            witness=dict(id=specification['id'],mod_key=target['key'],jar_sha256=target['sha256'],
                         entry=entry,entry_sha256=byte_hash(data))
            if entry.endswith('.class'):
                annotated=specification.get('include_annotations',False)
                parsed=ClassFile(data,retain_annotations=annotated)
                witness.update(class_name=parsed.name,superclass=parsed.super,interfaces=parsed.interfaces,methods=[])
                if annotated:witness['annotations']=parsed.annotations(parsed.attributes)
                if specification.get('include_declared_methods'):
                    witness['declared_method_names']=sorted({m['name'] for m in parsed.methods})
                for selection in specification['methods']:
                    name=selection['name'] if isinstance(selection,dict) else selection
                    methods=[m for m in parsed.methods if m['name']==name and
                        (not isinstance(selection,dict) or 'descriptor' not in selection or m['descriptor']==selection['descriptor'])]
                    assert methods, f'{entry}: missing {name}'
                    for m in methods:
                        ranges=selection.get('ranges') if isinstance(selection,dict) else None
                        if isinstance(selection,dict):
                            from collect_cataclysm_ignited_revenant_offense import instructions
                            body=instructions(parsed,m.get('code',b''))
                        else:
                            body=list(parsed.instructions(m.get('code',b'')))
                        if ranges:
                            body=[i for i in body if any(a<=i['offset']<=b for a,b in ranges)]
                            assert all(any(i['offset']==point for i in body) for span in ranges for point in span)
                        witness['methods'].append(dict(name=name,descriptor=m['descriptor'],
                            code_sha256=byte_hash(m.get('code',b'')),instructions=body,
                            **({'annotations':m['annotations']} if annotated else {}),
                            **({'instruction_offset_ranges':ranges} if ranges else {})))
            elif entry.endswith('.json'):
                witness['data']=json.loads(data)
            else:
                witness['text']=data.decode('utf-8')
            witnesses.append(witness)
    return dict(schema='tno.external_effects.native_evidence.v1',baseline=BASELINE,
                status='STATIC_EVIDENCE',witnesses=witnesses,
                note='Bytecode witnesses anchor manually reviewed native claims. Static evidence is not runtime validation, final vanilla comparison or completeness proof.')

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('mod_key');args=parser.parse_args()
    document=read_json(OUT/'native-findings'/f'{args.mod_key}.json')
    result=collect(document)
    write_json(OUT/'native-evidence'/f'{args.mod_key}.json',result)
    print(f'{args.mod_key}: {len(result["witnesses"])} installed-JAR witnesses pinned')
