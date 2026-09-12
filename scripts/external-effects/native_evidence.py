"""Pin manually reviewed claims to installed class/method bytes and archive resources."""
from classfile import ClassFile
from catalog_common import *

def collect(document):
    inventory=read_json(OUT/'jar-inventory.json')
    targets={x['key']:x for x in inventory['targets']+inventory['compat_candidates']}
    witnesses=[]
    for specification in document['evidence_specifications']:
        target=targets[specification['mod_key']]
        assert sha256(target['path'])==target['sha256']
        with zipfile.ZipFile(target['path']) as jar:
            entry=specification['entry']; data=jar.read(entry)
            witness=dict(id=specification['id'],mod_key=target['key'],jar_sha256=target['sha256'],
                         entry=entry,entry_sha256=byte_hash(data))
            if entry.endswith('.class'):
                parsed=ClassFile(data)
                witness.update(class_name=parsed.name,superclass=parsed.super,interfaces=parsed.interfaces,methods=[])
                for name in specification['methods']:
                    methods=[m for m in parsed.methods if m['name']==name]
                    assert methods, f'{entry}: missing {name}'
                    for m in methods:
                        witness['methods'].append(dict(name=name,descriptor=m['descriptor'],
                            code_sha256=byte_hash(m.get('code',b'')),
                            instructions=list(parsed.instructions(m.get('code',b'')))))
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
