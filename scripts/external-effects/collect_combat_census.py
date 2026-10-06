"""Recover an existing discovery index and capture one finite native call queue.

No classification or completion is inferred. The optional discovery observer
uses the same class parse/instruction pass, rather than scanning the JAR again.
Later consumers select exact methods from this queue; only reproduction may
repeat this deterministic foundation pass.
"""
import argparse
from collections import Counter
from pathlib import Path
import json

from catalog_common import OUT, WORK, BASELINE, read_json, write_json, sha256, byte_hash
from classfile import Reader
from discover import scan, COMBAT

INVOKE_OPS={'0xb6','0xb7','0xb8','0xb9','0xba'}
OVERRIDES={'hurt','isInvulnerableTo','canBeAffected','actuallyHurt','doHurtTarget',
    'onHitEntity','onHitBlock','onHit','applyEffectTick','isDurationEffectTick',
    'shouldApplyEffectTickThisTick','hurtEnemy','postHurtEnemy','releaseUsing',
    'use','finishUsingItem','getDefaultAttributeModifiers','getAttributeModifiers',
    'mobInteract','isAlliedTo','tickDeath','die','killedEntity','aiStep',
    'customServerAiStep','registerGoals','createAttributes','createLivingAttributes',
    'addAdditionalSaveData','readAdditionalSaveData'}


def structural_disposition(method, body, hits):
    if not method.get('code'):
        return 'DECLARATION_CONTEXT'
    if method['access'] & 0x1040 == 0x1040:
        return 'SYNTHETIC_BRIDGE_CONTEXT'
    ops=[i['opcode'] for i in body]
    if len(ops)<=4 and ops and ops[-1] in {'0xac','0xad','0xae','0xaf','0xb0'} \
            and all(o in {'0x2a','0xb4','0xb2','0xc0','0xac','0xad','0xae','0xaf','0xb0'} for o in ops):
        return 'FIELD_ACCESS_CONTEXT'
    if hits or method['name'] in OVERRIDES:
        return 'PENDING_SEMANTIC_REVIEW'
    return 'CALL_GRAPH_CONTEXT'


def observe(classes, methods, registrations):
    def capture(entry, raw, cls, bodies):
        classes.append(dict(entry=entry,entry_sha256=byte_hash(raw),name=cls.name,
            superclass=cls.super,interfaces=cls.interfaces,
            fields=[{k:v for k,v in f.items() if k!='code'} for f in cls.fields]))
        for method in cls.methods:
            body=bodies.get((method['name'],method['descriptor']),[])
            hits=[i for i in body if isinstance(i['operand'],str) and COMBAT.search(i['operand'])]
            methods.append(dict(entry=entry,method=method['name'],descriptor=method['descriptor'],
                access=method['access'],code_sha256=byte_hash(method.get('code',b'')),
                code_bytes=len(method.get('code',b'')),
                disposition=structural_disposition(method,body,hits),
                hits=hits,calls=[i for i in body if i['opcode'] in INVOKE_OPS]))
        for name,data in cls.attributes:
            if name!='BootstrapMethods':
                continue
            r=Reader(data)
            for index in range(r.u2()):
                handle=cls.resolve(r.u2());args=[cls.resolve(r.u2()) for _ in range(r.u2())]
                registrations.append(dict(entry=entry,index=index,handle=handle,arguments=args))
    return capture


def pack_sites(document):
    """Intern repeated native symbols without dropping any instruction site."""
    symbols=sorted({i['operand'] for m in document['methods'] for k in ('hits','calls') for i in m[k]})
    by_symbol={value:index for index,value in enumerate(symbols)}
    for method in document['methods']:
        for key in ('hits','calls'):
            method[key]=[[i['offset'],int(i['opcode'],16),by_symbol[i['operand']]] for i in method[key]]
    document['instruction_site_encoding']=['offset','opcode','symbol_index']
    document['symbols']=symbols
    return document


def decode_sites(document, method, key='hits'):
    return [dict(offset=offset,opcode=hex(opcode),operand=document['symbols'][symbol])
            for offset,opcode,symbol in method[key]]


def write_census(path, document):
    """One compact object per row: deterministic JSON without giant prose/lines."""
    arrays=('classes','methods','registration_bootstraps','symbols')
    header=json.dumps({k:v for k,v in document.items() if k not in arrays},ensure_ascii=False,indent=2)
    chunks=[header[:-2]]
    for key in arrays:
        chunks.append(',\n  '+json.dumps(key)+': [\n')
        chunks.append(',\n'.join('    '+json.dumps(v,ensure_ascii=False,separators=(',',':')) for v in document[key]))
        chunks.append('\n  ]')
    Path(path).write_text(''.join(chunks)+'\n}\n',encoding='utf-8')


def collect(mod_key, jar):
    target=next(t for t in read_json(OUT/'jar-inventory.json')['targets'] if t['key']==mod_key)
    jar=Path(jar)
    assert sha256(jar)==target['sha256'] and jar.stat().st_size==target['size_bytes'], 'Pinned source mismatch'
    # Historical detailed indexes were intentionally untracked. Recover the
    # same artifacts while adding call-graph context in this single parse pass.
    classes=[];methods=[];registrations=[]
    locator=OUT/'discovery'/f'{mod_key}-scan.json'
    original_bytes=locator.read_bytes();original=read_json(locator)
    try:
        discovered=scan(dict(target,path=str(jar)),observe(classes,methods,registrations))
    finally:
        locator.write_bytes(original_bytes)
    assert discovered['parsed_classes']==original['parsed_classes']==target['classes']
    assert not discovered['parse_errors']
    old_hashes={Path(a['path']).name:a['sha256'] for a in original['index_artifacts']}
    for artifact in discovered['index_artifacts']:
        expected=old_hashes[Path(artifact['path']).name]
        if artifact['sha256']!=expected:
            # Original indexes were written on Windows. Recover their exact
            # CRLF bytes, rather than treating a newline change as new research.
            path=WORK/mod_key/Path(artifact['path']).name
            windows=path.read_bytes().replace(b'\n',b'\r\n')
            assert byte_hash(windows)==expected, 'Discovery recovery differs from original pinned index'
            path.write_bytes(windows)
    # Keep the protected locator summary unchanged: only new census evidence is
    # committed, and recovered detailed indexes stay in the existing run cache.
    counts=dict(sorted(Counter(m['disposition'] for m in methods).items()))
    return pack_sites(dict(schema='tno.external_effects.combat_census.v1',baseline=BASELINE,
        mod_key=mod_key,jar_sha256=target['sha256'],jar_size_bytes=target['size_bytes'],
        prior_discovery_file=f'discovery/{mod_key}-scan.json',
        prior_index_recovery='BYTE_IDENTICAL',parsed_classes=len(classes),
        total_methods=len(methods),counts_by_disposition=counts,
        scope='Finite instruction/call/registration census. Context dispositions are not exclusions or semantic completion; native producers and reachable dependencies still require evidence-backed review.',
        classes=classes,methods=methods,registration_bootstraps=registrations,
        resource_index=dict(path=(WORK/mod_key/'resources.json').relative_to(WORK.parent.parent).as_posix(),
            sha256=sha256(WORK/mod_key/'resources.json'))))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mod_key');parser.add_argument('jar',type=Path)
    args=parser.parse_args();result=collect(args.mod_key,args.jar)
    write_census(OUT/f'{args.mod_key}-combat-census.json',result)
    print({k:result[k] for k in ['mod_key','parsed_classes','total_methods','counts_by_disposition','prior_index_recovery']})
