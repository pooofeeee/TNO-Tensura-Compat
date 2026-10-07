"""Pin manually reviewed claims to installed class/method bytes and archive resources."""
from classfile import ClassFile
from catalog_common import *


def annotate_local_operands(body, code):
    """Retain exact variable slots where actor identity needs independent proof."""
    for instruction in body:
        offset = instruction['offset']
        opcode = code[offset]
        if opcode in range(0x15, 0x1a) or opcode in range(0x36, 0x3b) or opcode in (0x84, 0xa9):
            instruction['local_index'] = code[offset + 1]
            if opcode == 0x84:
                instruction['increment'] = int.from_bytes(code[offset+2:offset+3], 'big', signed=True)
        elif 0x1a <= opcode <= 0x2d:
            instruction['local_index'] = (opcode - 0x1a) % 4
        elif 0x3b <= opcode <= 0x4e:
            instruction['local_index'] = (opcode - 0x3b) % 4
        elif opcode == 0xc4:
            instruction['local_opcode'] = hex(code[offset + 1])
            instruction['local_index'] = int.from_bytes(code[offset+2:offset+4], 'big')
            if code[offset + 1] == 0x84:
                instruction['increment'] = int.from_bytes(code[offset+4:offset+6], 'big', signed=True)
    return body

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
                metadata=any(isinstance(s,dict) and s.get('include_exception_handlers')
                             for s in specification['methods'])
                parsed=ClassFile(data,retain_annotations=annotated,retain_code_metadata=metadata)
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
                        if isinstance(selection, dict) and selection.get('include_local_operands'):
                            annotate_local_operands(body, m.get('code', b''))
                        if ranges:
                            body=[i for i in body if any(a<=i['offset']<=b for a,b in ranges)]
                            assert all(any(i['offset']==point for i in body) for span in ranges for point in span)
                        witness['methods'].append(dict(name=name,descriptor=m['descriptor'],
                            code_sha256=byte_hash(m.get('code',b'')),instructions=body,
                            **({'annotations':m['annotations']} if annotated else {}),
                            **({'exception_handlers':[dict(start=a,end=b,handler=h,
                                catch_type=parsed.resolve(t)) for a,b,h,t in m.get('exception_handlers',[])]}
                               if isinstance(selection,dict) and selection.get('include_exception_handlers') else {}),
                            **({'instruction_offset_ranges':ranges} if ranges else {})))
            elif entry.endswith('.json'):
                witness['data']=json.loads(data)
            elif entry.endswith('.nbt') and specification.get('structure_payload_projection'):
                import gzip
                from structure_nbt import decode, payload_projection
                raw = gzip.decompress(data) if data.startswith(b'\x1f\x8b') else data
                witness['structure_payload'] = payload_projection(decode(raw))
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
